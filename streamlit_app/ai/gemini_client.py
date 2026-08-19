"""
Google Gemini access for the AI Assistant.

Uses the official google-genai SDK and config.GEMINI_MODEL only.
The API key is read from Streamlit secrets or the environment and is
never written to source code, logs or SQL Server.
"""

import json
import os
import re
import threading
import time

import config


MISSING_KEY_MESSAGE = config.MISSING_GEMINI_KEY_MESSAGE

_JSON_FENCE = re.compile(
    r"^```(?:json)?\s*(.*?)\s*```$",
    re.DOTALL | re.IGNORECASE,
)


# Keyed by API key so the httpx connection pool is reused across reruns.
_CLIENT_CACHE = {}

_CLIENT_LOCK = threading.Lock()


class GeminiError(RuntimeError):
    """Raised when Gemini cannot be called or returns an unusable result."""


def _log(message):
    """Write a diagnostic line to the Streamlit / console process."""

    print(f"[AI Assistant] {message}", flush=True)


def get_gemini_api_key():
    """
    Return GEMINI_API_KEY from the environment or Streamlit secrets.

    An empty string means the key is not configured. Missing secrets
    files are treated as "not configured", not as a crash.
    """

    environment_key = os.environ.get(config.GEMINI_API_KEY_NAME, "")

    if environment_key and environment_key.strip():

        return environment_key.strip()

    try:

        import streamlit as st

        secret_key = st.secrets[config.GEMINI_API_KEY_NAME]

    except Exception:

        return ""

    if secret_key is None:

        return ""

    return str(secret_key).strip()


def generate_text(prompt, system_instruction=None, expect_json=False):
    """
    Call the configured Gemini model and return the response text.

    Does not contact Gemini when the API key is missing.
    """

    api_key = get_gemini_api_key()

    if not api_key:

        raise GeminiError(MISSING_KEY_MESSAGE)

    try:

        from google import genai
        from google.genai import types

    except ImportError as error:

        raise GeminiError(
            "The google-genai package is not installed."
        ) from error

    generation_config = {
        "temperature": 0,
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(
            disable=True,
            maximum_remote_calls=None,
        ),
    }

    if system_instruction:

        generation_config["system_instruction"] = system_instruction

    if expect_json:

        generation_config["response_mime_type"] = "application/json"

    _log("Gemini request start")
    started = time.perf_counter()
    timeout_seconds = max(config.AI_GEMINI_TIMEOUT_MS / 1000.0, 1)
    outcome = {}
    done = threading.Event()

    def _worker():

        try:

            outcome["response"] = _generate_content(
                genai,
                types,
                api_key,
                prompt,
                generation_config,
            )

        except Exception as error:

            outcome["error"] = error

            _log(
                f"Gemini worker error after {time.perf_counter() - started:.1f}s: "
                f"{type(error).__name__}: {error}"
            )

        finally:

            done.set()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    try:

        if not done.wait(timeout=timeout_seconds):

            raise GeminiError(
                "The Gemini API request timed out. This is a Gemini API "
                "delay, not a SQL Server problem. Please try again."
            )

        if "error" in outcome:

            raise outcome["error"]

        response = outcome["response"]

    except GeminiError:

        _log(
            "Gemini request failed after "
            f"{time.perf_counter() - started:.1f}s"
        )
        raise

    except Exception as error:

        _log(
            "Gemini request failed after "
            f"{time.perf_counter() - started:.1f}s"
        )
        raise GeminiError(_friendly_gemini_error(error)) from error

    _log(
        "Gemini response completion in "
        f"{time.perf_counter() - started:.1f}s"
    )

    text = (getattr(response, "text", None) or "").strip()

    if not text:

        raise GeminiError("Gemini returned an empty response.")

    return text


def _build_client(genai, types, api_key):
    """
    Return a cached Gemini client, pinned to IPv4 when configured.

    google-genai passes http_options.client_args straight to its httpx
    client, and httpx binds the socket to the given local address. An IPv4
    local address makes httpx resolve and connect over IPv4 only, so the
    dead IPv6 routes for the Google API host are never attempted.
    """

    with _CLIENT_LOCK:

        cached = _CLIENT_CACHE.get(api_key)

        if cached is not None:

            return cached

        client_args = {}

        if config.AI_GEMINI_FORCE_IPV4:

            import httpx

            client_args["transport"] = httpx.HTTPTransport(
                local_address="0.0.0.0",
            )

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=config.AI_GEMINI_TIMEOUT_MS,
                client_args=client_args or None,
            ),
        )

        _log(
            f"Gemini client created for {config.GEMINI_MODEL} "
            f"(force_ipv4={bool(client_args)})"
        )

        _CLIENT_CACHE[api_key] = client

        return client


def _generate_content(genai, types, api_key, prompt, generation_config):
    """Run the Gemini generate_content call in a worker thread."""

    client = _build_client(genai, types, api_key)

    return client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(**generation_config),
    )


def parse_json_object(text):
    """Parse a JSON object from a model response."""

    candidate = text.strip()
    fenced = _JSON_FENCE.match(candidate)

    if fenced:

        candidate = fenced.group(1).strip()

    try:

        payload = json.loads(candidate)

    except json.JSONDecodeError as error:

        raise GeminiError(
            "Gemini did not return valid JSON for the warehouse query."
        ) from error

    if not isinstance(payload, dict):

        raise GeminiError(
            "Gemini did not return a JSON object for the warehouse query."
        )

    return payload


def _friendly_gemini_error(error):
    """Map SDK/API failures to a safe user-facing message."""

    detail = str(error).lower()

    # Quota is checked first so a rate-limit reply is never reported as a
    # timeout, and the message names Gemini so it is not read as a warehouse
    # or SQL Server failure.
    if any(
        token in detail
        for token in ("429", "quota", "rate limit", "resource_exhausted")
    ):

        return (
            "The Gemini API rate limit or quota was exceeded. This is a "
            "Gemini API limit, not a SQL Server or warehouse problem. "
            "Please wait a moment and ask again."
        )

    if any(
        token in detail
        for token in ("503", "unavailable", "high demand", "overloaded")
    ):

        return (
            "The Gemini model is temporarily overloaded. "
            "Please try again in a moment."
        )

    # 499 CANCELLED is returned when the request exceeds the server timeout
    # the SDK derives from AI_GEMINI_TIMEOUT_MS.
    if any(
        token in detail
        for token in ("timeout", "timed out", "deadline", "499", "cancelled")
    ):

        return (
            "The Gemini API request timed out. This is a Gemini API delay, "
            "not a SQL Server problem. Please try again."
        )

    if any(
        token in detail
        for token in ("401", "403", "api key", "permission", "unauthenticated")
    ):

        return (
            "The Gemini API key was rejected. Check that GEMINI_API_KEY "
            "is configured correctly."
        )

    return "The Gemini API request failed. Please try again."
