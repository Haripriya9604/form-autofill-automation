# fix_clean_and_emails.py
# Run inside your virtualenv in the folder with your CSV.
# Produces: alumni_dataset_2017_2021_cleaned_human_fixed.csv

import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

IN = "alumni_dataset_2017_2021_cleaned_human.csv"
OUT = "alumni_dataset_2017_2021_cleaned_human_fixed.csv"

# Columns we expect (safe default list)
LIKERT_COLS = [
    "Education prepared me well",
    "Progressed in career",
    "Apply engineering principles",
    "Solve complex problems",
    "Consider broader societal issues",
    "Stay current with technologies",
    "Responsive to global issues"
]

EXPECTED = [
    "Email","Name","Department","Stream","Year of Graduation","Current Job Title and Employer",
    "Years Working","Education prepared me well","Progressed in career","Apply engineering principles",
    "Solve complex problems","Consider broader societal issues","Stay current with technologies",
    "Responsive to global issues","University helped","Areas to improve"
]

# canonical mapping for likert answers
CANONICAL = {
    "strongly agree": "Strongly agree",
    "stronglyagree": "Strongly agree",
    "strongly agree.": "Strongly agree",
    "strongly agree ": "Strongly agree",
    "strongly agrees": "Strongly agree",
    "strongly agree\t": "Strongly agree",
    "strongly agree\n": "Strongly agree",
    "strongly agree\r": "Strongly agree",
    "strongly agree.": "Strongly agree",
    "agree": "Agree",
    "neutral": "Neutral",
    "disagree": "Disagree"
}

def clean_text(s):
    if pd.isna(s): return ""
    s = str(s)
    s = s.replace("\t"," ").replace("\r"," ").replace("\n"," ")
    s = re.sub(r'\s+', ' ', s)   # collapse multiple spaces
    return s.strip()

def normalize_name(name):
    name = clean_text(name)
    # Title case but keep uppercase acronyms (naively)
    # We'll do a basic title() which is fine for most names
    return ' '.join([part.capitalize() for part in name.split()]) if name else ""

def safe_email_from_name(name):
    # build base from name parts, keep only a-z0-9
    parts = re.findall(r"[a-z0-9]+", name.lower())
    if not parts:
        return ""
    base = '.'.join(parts)
    return f"{base}@gmail.com"

def canonical_likert(v):
    v0 = clean_text(v).lower()
    return CANONICAL.get(v0, v if v else "")

def ensure_numeric_year(s, default="2021"):
    s = clean_text(s)
    digits = re.findall(r'\d{4}', s)
    if digits:
        return digits[0]
    # fallback to 4-digit default
    return default

def ensure_years_working(s, default="4"):
    s = clean_text(s)
    m = re.search(r'\d+', s)
    return m.group(0) if m else default

def main():
    p = Path(IN)
    if not p.exists():
        print("Input file not found:", IN)
        return
    df = pd.read_csv(p, dtype=str).fillna("")
    n_rows = len(df)
    print(f"Loaded {n_rows} rows from {IN}")

    # Trim and normalize columns that exist
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    # Normalize names if present
    if "Name" in df.columns:
        df["Name"] = df["Name"].apply(normalize_name)

    # Normalize job/company
    if "Current Job Title and Employer" in df.columns:
        df["Current Job Title and Employer"] = df["Current Job Title and Employer"].apply(clean_text)

    # Normalize textual columns:
    for col in ["Department","Stream","University helped","Areas to improve"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # Normalize Likert columns
    for col in LIKERT_COLS:
        if col in df.columns:
            df[col] = df[col].apply(canonical_likert)

    # Year and Years Working
    if "Year of Graduation" in df.columns:
        df["Year of Graduation"] = df["Year of Graduation"].apply(lambda x: ensure_numeric_year(x, default="2021"))
    if "Years Working" in df.columns:
        df["Years Working"] = df["Years Working"].apply(lambda x: ensure_years_working(x, default="4"))

    # Emails: clean, lower, fill missing from name, ensure uniqueness
    if "Email" not in df.columns:
        df["Email"] = ""

    # clean emails
    df["Email"] = df["Email"].apply(lambda s: clean_text(s).lower())

    # generate where missing
    for idx, row in df[df["Email"] == ""].iterrows():
        generated = safe_email_from_name(row.get("Name",""))
        df.at[idx, "Email"] = generated

    # ensure uniqueness: if duplicates, append number before @
    counts = defaultdict(int)
    final_emails = []
    for e in df["Email"]:
        if not e:
            final_emails.append(e)
            continue
        if "@" in e:
            local, domain = e.split("@",1)
        else:
            local, domain = e, "gmail.com"
        key = (local, domain)
        counts[key] += 1
        if counts[key] == 1:
            final_emails.append(f"{local}@{domain}")
        else:
            # append numeric suffix
            final_emails.append(f"{local}{counts[key]}@{domain}")
    df["Email"] = final_emails

    # Report duplicates (should be none)
    dup_count = df["Email"].duplicated().sum()
    print(f"After uniqueness pass, duplicate emails count: {dup_count}")

    # Reorder columns to EXPECTED where present
    ordered = [c for c in EXPECTED if c in df.columns]
    extras = [c for c in df.columns if c not in ordered]
    df_final = df[ordered + extras]

    df_final.to_csv(OUT, index=False)
    print(f"Wrote cleaned file: {OUT}")
    print("\nSample rows (first 6):")
    print(df_final.head(6).to_string(index=False))
    # quick checks summary
    print("\nSummary:")
    print(" Rows:", len(df_final))
    print(" Unique emails:", df_final['Email'].nunique())
    empty_n = df_final[expected_missing_cols := [c for c in EXPECTED if c not in df_final.columns]].shape[0] if expected_missing_cols else 0
    if expected_missing_cols:
        print("WARNING: These expected columns are missing from final output:", expected_missing_cols)
    print("Done.")

if __name__ == '__main__':
    main()
