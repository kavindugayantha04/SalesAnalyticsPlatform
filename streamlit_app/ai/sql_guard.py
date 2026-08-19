"""
Validate Gemini-generated SQL before it reaches SQL Server.

Only a single read-only SELECT against the allowed warehouse objects
may run. This module never opens a database connection.
"""

import re


from .schema import ALLOWED_OBJECTS


FORBIDDEN_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "EXEC",
    "EXECUTE",
    "GRANT",
    "REVOKE",
    "BACKUP",
    "RESTORE",
    "SHUTDOWN",
    "WAITFOR",
    "OPENROWSET",
    "OPENDATASOURCE",
    "OPENQUERY",
    "SP_EXECUTESQL",
    "XP_",
    "INFORMATION_SCHEMA",
)

_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)
_COMMENT_LINE = re.compile(r"--[^\n]*")
_STRING_LITERAL = re.compile(r"'(?:''|[^'])*'")
_OBJECT_NAME = re.compile(
    r"\b(dw|dbo)\s*\.\s*\[?([A-Za-z_][A-Za-z0-9_]*)\]?",
    re.IGNORECASE,
)
_KEYWORD = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|CREATE|TRUNCATE|"
    r"EXEC(?:UTE)?|GRANT|REVOKE|BACKUP|RESTORE|SHUTDOWN|WAITFOR|"
    r"OPENROWSET|OPENDATASOURCE|OPENQUERY|SP_EXECUTESQL)\b",
    re.IGNORECASE,
)
_SELECT_INTO = re.compile(r"\bINTO\b", re.IGNORECASE)
_LEADING_KEYWORD = re.compile(r"^(SELECT|WITH)\b", re.IGNORECASE)
_SELECT_STAR = re.compile(
    r"\bSELECT\s+(?:TOP\s+\d+\s+(?:PERCENT\s+)?)?\*",
    re.IGNORECASE,
)
_HAS_TOP = re.compile(r"\bSELECT\s+TOP\s+\d+\b", re.IGNORECASE)
_HAS_AGGREGATE = re.compile(
    r"\b(?:SUM|COUNT|AVG|MIN|MAX)\s*\(",
    re.IGNORECASE,
)
_HAS_GROUP_BY = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)

# A join without a condition multiplies the fact table by the dimension and
# cannot complete inside the query timeout.
_JOIN = re.compile(r"\bJOIN\b", re.IGNORECASE)
_JOIN_ON = re.compile(r"\bON\b", re.IGNORECASE)
_CROSS_JOIN = re.compile(r"\bCROSS\s+(?:JOIN|APPLY)\b", re.IGNORECASE)
_IMPLICIT_JOIN = re.compile(
    r"\bFROM\s+(?:dw|dbo)\s*\.\s*\[?[A-Za-z_][A-Za-z0-9_]*\]?"
    r"(?:\s+(?:AS\s+)?[A-Za-z_][A-Za-z0-9_]*)?\s*,",
    re.IGNORECASE,
)

ALLOWED_LOOKUP = {name.lower() for name in ALLOWED_OBJECTS}


class UnsafeSQLError(ValueError):
    """Raised when generated SQL is not a safe warehouse SELECT."""


def validate_readonly_sql(sql):
    """
    Return cleaned SQL if it is a single allowed SELECT.

    Raises UnsafeSQLError otherwise.
    """

    if sql is None or not str(sql).strip():

        raise UnsafeSQLError("The model did not return a SQL query.")

    cleaned = _strip_comments(str(sql)).strip().rstrip(";").strip()

    if not cleaned:

        raise UnsafeSQLError("The generated SQL was empty.")

    if ";" in cleaned:

        raise UnsafeSQLError("Multiple SQL statements are not allowed.")

    if not _LEADING_KEYWORD.search(cleaned):

        raise UnsafeSQLError("Only SELECT queries are allowed.")

    if _KEYWORD.search(cleaned):

        raise UnsafeSQLError("The generated SQL contains a forbidden statement.")

    if _SELECT_INTO.search(_mask_strings(cleaned)):

        raise UnsafeSQLError("SELECT INTO is not allowed.")

    lowered = cleaned.lower()

    if "information_schema" in lowered or "xp_" in lowered:

        raise UnsafeSQLError("System catalog queries are not allowed.")

    objects = _referenced_objects(cleaned)

    if not objects:

        raise UnsafeSQLError(
            "The query must reference an allowed dw warehouse object."
        )

    for schema, name in objects:

        qualified = f"{schema}.{name}".lower()

        if schema.lower() != "dw" or qualified not in ALLOWED_LOOKUP:

            raise UnsafeSQLError(
                "The query references an object that is not allowed."
            )

    _validate_joins(cleaned)

    fact_sales_used = any(
        schema.lower() == "dw" and name.lower() == "factsales"
        for schema, name in objects
    )

    if fact_sales_used and _SELECT_STAR.search(cleaned):

        raise UnsafeSQLError(
            "Full-table reads of dw.FactSales are not allowed."
        )

    if fact_sales_used and not (
        _HAS_AGGREGATE.search(cleaned)
        or _HAS_TOP.search(cleaned)
        or _HAS_GROUP_BY.search(cleaned)
    ):

        raise UnsafeSQLError(
            "dw.FactSales queries must use aggregates or TOP."
        )

    return cleaned


def _validate_joins(sql):
    """
    Require an explicit condition for every join.

    Cross joins, comma-separated table lists and JOIN without ON produce a
    cartesian product over the fact table, which never finishes.
    """

    masked = _mask_strings(sql)

    if _CROSS_JOIN.search(masked):

        raise UnsafeSQLError(
            "Cross joins are not allowed. Use JOIN ... ON with warehouse keys."
        )

    if _IMPLICIT_JOIN.search(masked):

        raise UnsafeSQLError(
            "Comma-separated tables are not allowed. "
            "Use JOIN ... ON with warehouse keys."
        )

    if len(_JOIN.findall(masked)) > len(_JOIN_ON.findall(masked)):

        raise UnsafeSQLError(
            "Every JOIN must have an ON condition using the warehouse keys."
        )


def _strip_comments(sql):
    """Remove block and line comments before validation."""

    without_blocks = _COMMENT_BLOCK.sub(" ", sql)

    return _COMMENT_LINE.sub(" ", without_blocks)


def _mask_strings(sql):
    """Replace string literals so keyword checks ignore quoted text."""

    return _STRING_LITERAL.sub("''", sql)


def _referenced_objects(sql):
    """Return (schema, object) pairs referenced with a schema prefix."""

    return [
        (match.group(1), match.group(2))
        for match in _OBJECT_NAME.finditer(sql)
    ]
