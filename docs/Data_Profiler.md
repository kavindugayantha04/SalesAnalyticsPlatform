# Data Profiler

## Overview

The Data Profiler is the first module of the Sales Analytics Platform.

Its purpose is to analyze raw datasets before they enter the ETL pipeline and SQL Server.

This module helps identify potential data quality issues early in the process.

---

## Objectives

- Detect available datasets
- Read CSV files
- Count rows and columns
- Display column names
- Identify data types
- Detect missing values
- Detect duplicate rows
- Calculate memory usage

---

## Current Features (Version 1)

✅ Scan the `data/raw` folder

✅ Read all CSV files automatically

✅ Display:

- Dataset Name
- Number of Rows
- Number of Columns
- Column Names
- Data Types
- Missing Values
- Duplicate Rows
- Memory Usage

---

## Current Workflow

```text
Raw CSV Files
        │
        ▼
Data Profiler
        │
        ▼
Profiling Report
```

---

## Input

CSV files stored in:

```
data/raw/
```

---

## Output

Console report showing:

- Dataset information
- Column summary
- Missing values
- Duplicate rows
- Memory usage

---

## Future Improvements

- Export report to CSV
- Export report to HTML
- Generate Markdown report
- Detect Primary Keys
- Detect Foreign Keys
- Validate uploaded Excel files
- Integrate with Streamlit

---

## Module Status

Completed ✅ (Version 1)