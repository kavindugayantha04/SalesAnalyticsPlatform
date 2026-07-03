import os
import pandas as pd

DATA_FOLDER = "data/raw"


def get_csv_files(folder_path):
    """
    Returns a list of all CSV files in the specified folder.
    """

    csv_files = []

    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            csv_files.append(file)

    return csv_files


def main():

    print("=" * 60)
    print("Sales Analytics Platform")
    print("Data Profiler")
    print("=" * 60)

    print(f"\nScanning folder: {DATA_FOLDER}\n")

    csv_files = get_csv_files(DATA_FOLDER)

    print(f"Found {len(csv_files)} datasets.\n")

    for file in csv_files:
        print(file)


if __name__ == "__main__":
    main()