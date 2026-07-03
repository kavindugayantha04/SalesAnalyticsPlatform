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


def profile_dataset(file_path):
    """
    Reads a dataset and returns basic profiling information.
    """

    df = pd.read_csv(file_path)

    report = {
        "Dataset": os.path.basename(file_path),
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Column Names": list(df.columns),
        "Data Types": df.dtypes.astype(str).to_dict(),
        "Missing Values": df.isnull().sum().to_dict(),
        "Duplicate Rows": int(df.duplicated().sum()),
        "Memory Usage (MB)": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
    }

    return report


def display_report(report):
    """
    Displays the profiling report.
    """

    print("=" * 60)
    print(f"Dataset : {report['Dataset']}")
    print("=" * 60)

    print(f"Rows            : {report['Rows']}")
    print(f"Columns         : {report['Columns']}")
    print(f"Duplicate Rows  : {report['Duplicate Rows']}")
    print(f"Memory Usage    : {report['Memory Usage (MB)']} MB")

    print("\nColumn Summary")
    print("-" * 60)

    for column in report["Column Names"]:

        dtype = report["Data Types"][column]
        missing = report["Missing Values"][column]

        print(f"{column:<35} {dtype:<10} Missing: {missing}")

    print("\n")


def main():

    print("=" * 60)
    print("Sales Analytics Platform")
    print("Data Profiler")
    print("=" * 60)

    print(f"\nScanning folder: {DATA_FOLDER}\n")

    csv_files = get_csv_files(DATA_FOLDER)

    print(f"Found {len(csv_files)} datasets.\n")

    for file in csv_files:

        full_path = os.path.join(DATA_FOLDER, file)

        report = profile_dataset(full_path)

        display_report(report)


if __name__ == "__main__":
    main()