# 🚀 Automated Google Form Filler (Python + PowerShell)

This project automates **bulk submissions to Google Forms** from CSV/Excel datasets.  
It was applied to alumni feedback forms (300+ entries), but works for **any form with similar structure**.

---

## ✨ Features
- 🔗 Maps spreadsheet fields → Google Form `entry.XXXXXXX` IDs  
- 📤 Auto-fills & submits responses in bulk (supports chunking for large datasets)  
- 📝 Dry-run mode for safe testing (no actual submission)  
- ⚡ Batch execution with PowerShell scripts to avoid overloading  
- ✅ Logs every submission (status codes + payloads)

---

## 📊 Example Workflow

### 1. Prepare your dataset
Start with a **human-readable CSV** (`sample_input.csv`):

```csv
Name,Department,Stream,Year of Graduation,Current Job Title and Employer,Years Working,University helped,Areas to improve,Education prepared me well,Progressed in career,Apply engineering principles,Solve complex problems,Consider broader societal issues,Stay current with technologies,Responsive to global issues,Email
Alice Example,CSE,Computer Science and Engineering,2023,Acme Corp,2,Strongly agree,Update labs,Agree,Agree,Strongly agree,Agree,Neutral,Agree,Agree,alice.example@gmail.com
Bob Sample,CSE,Computer Science and Engineering,2022,Example Inc,3,Agree,More internships,Agree,Strongly agree,Agree,Strongly agree,Agree,Neutral,Agree,bob.sample@gmail.com

---

## 🛠 Tech Stack
- 🐍 Python **3.11+**  
- 📊 Pandas (data wrangling)  
- 🌐 Requests (HTTP submissions)  
- 💻 PowerShell (automation scripting)  

---

## 📂 Project Structure
