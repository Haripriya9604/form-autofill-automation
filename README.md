# 🚀 Automated Google Form Submission Tool  
**Bulk Google Form Responses via CSV/Excel (Python + PowerShell)**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?logo=pandas&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP%20Client-000000)
![PowerShell](https://img.shields.io/badge/PowerShell-Automation-5391FE?logo=powershell&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Use%20Case](https://img.shields.io/badge/Use%20Case-Google%20Forms%20Automation-success)
![License](https://img.shields.io/badge/License-Educational%20%26%20Internal-orange)

---

## 📌 Overview
This project provides a **robust automation pipeline** for submitting **bulk responses to Google Forms** using structured data from CSV or Excel files.

It was originally developed to automate **300+ alumni feedback form submissions**, but the system is **form-agnostic** and can be adapted to **any Google Form** by configuring field mappings.

The solution is built with a focus on **scalability, safety, and traceability**, making it suitable for academic institutions, internal surveys, administrative workflows, and controlled data collection tasks.

---

## 🎯 Key Capabilities
- 🔗 **Field Mapping**  
  Map human-readable spreadsheet headers to Google Form `entry.XXXXXXX` field IDs.

- 📤 **Bulk & Chunked Submissions**  
  Submit large datasets in controlled batches to avoid rate limits or throttling.

- 🧪 **Dry-Run Mode**  
  Validate payloads and mappings without submitting data to the live form.

- ⚡ **PowerShell Automation**  
  Execute batch jobs and orchestration scripts in Windows environments.

- 📄 **Detailed Logging**  
  Logs HTTP status codes, request payloads, and submission outcomes for auditing and debugging.

- 🧹 **Data Cleaning Utilities**  
  Scripts for email validation, deduplication, and dataset normalization.
  
🧱 Tech Stack

Python 3.11+

Pandas – data cleaning and transformation

Requests – HTTP-based form submissions

PowerShell – batch execution and automation

🔄 Typical Workflow

Prepare dataset (CSV / Excel → CSV)

Clean and validate data

Map spreadsheet headers to Google Form entry IDs

Split data into manageable chunks

Run dry-run validation

Execute batch submissions

Review logs for verification and auditing

⚠️ Important Notes

This tool does not bypass Google authentication or security mechanisms.

Intended strictly for authorized, ethical, and internal use.

Excessive submission rates may trigger throttling—chunking is strongly recommended.

Users are responsible for complying with Google Forms’ terms of service.

## 👤 Author

**Name:** Haripriya S K  
**Role:** Software Engineering & Data Automation  
**Email:** haripriyask964@gmail.com  

---

## 📊 Input Format
The workflow begins with a **human-readable CSV** (Excel files can be converted to CSV).

### Example: `sample_input.csv`
```csv
Name,Department,Stream,Year of Graduation,Current Job Title and Employer,Years Working,University helped,Areas to improve,Education prepared me well,Progressed in career,Apply engineering principles,Solve complex problems,Consider broader societal issues,Stay current with technologies,Responsive to global issues,Email
Alice Example,CSE,Computer Science and Engineering,2023,Acme Corp,2,Strongly agree,Update labs,Agree,Agree,Strongly agree,Agree,Neutral,Agree,Agree,alice.example@gmail.com
Bob Sample,CSE,Computer Science and Engineering,2022,Example Inc,3,Agree,More internships,Agree,Strongly agree,Agree,Strongly agree,Agree,Neutral,Agree,bob.sample@gmail.com

Project Structure

├── auto_submit_gform.py        # Core Google Form submission logic
├── fix_clean_and_emails.py    # Data cleaning & email normalization
├── rename_entry_to_human.py   # Reverse mapping (entry IDs → readable headers)
├── map_and_chunk_alumini.py   # Field mapping + dataset chunking
├── post_chunk_poster.py       # Submit chunked CSV files
├── fetch_form_info.py         # Retrieve Google Form metadata
│
├── input/                     # Cleaned input datasets
├── mapped/                    # Mapped & chunked CSV files
├── logs/                      # Submission logs & responses
│
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

