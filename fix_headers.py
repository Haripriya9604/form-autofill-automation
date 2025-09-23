# fix_headers.py
# Usage: python fix_headers.py
# This script:
#  - reads alumni_dataset_2017_2021_cleaned.csv in current dir
#  - prints current headers
#  - attempts to map them to the exact expected headers using fuzzy matching
#  - writes a fixed file alumni_dataset_2017_2021_cleaned_fixed.csv

import pandas as pd
from difflib import get_close_matches
from pathlib import Path

IN = "alumni_dataset_2017_2021_cleaned.csv"
OUT = "alumni_dataset_2017_2021_cleaned_fixed.csv"

EXPECTED = [
    "Email",
    "Name",
    "Department",
    "Stream",
    "Year of Graduation",
    "Current Job Title and Employer",
    "Years Working",
    "Education prepared me well",
    "Progressed in career",
    "Apply engineering principles",
    "Solve complex problems",
    "Consider broader societal issues",
    "Stay current with technologies",
    "Responsive to global issues",
    "University helped",
    "Areas to improve"
]

def suggest_map(current_cols):
    mapping = {}
    remaining_expected = set(EXPECTED)
    for cur in current_cols:
        # try direct match first (case insensitive)
        for ex in EXPECTED:
            if cur.strip().lower() == ex.strip().lower():
                mapping[cur] = ex
                remaining_expected.discard(ex)
                break
        else:
            # fuzzy match
            candidates = get_close_matches(cur, EXPECTED, n=3, cutoff=0.6)
            if candidates:
                mapping[cur] = candidates[0]
                remaining_expected.discard(candidates[0])
            else:
                mapping[cur] = None
    return mapping, remaining_expected

def main():
    p = Path(IN)
    if not p.exists():
        print(f"Input file not found: {IN}")
        return
    df = pd.read_csv(p, dtype=str)
    cur = list(df.columns)
    print("Current headers in CSV:")
    for c in cur:
        print("  -", c)
    mapping, missing_expected = suggest_map(cur)
    print("\nSuggested mapping (current -> mapped):")
    for k,v in mapping.items():
        print(f"  {k!r}  ->  {v!r}")
    if missing_expected:
        print("\nExpected headers not matched yet (will be added as empty columns):")
        for m in missing_expected:
            print("  -", m)
    # Apply mapping: rename columns we can, keep others
    rename_dict = {k: v for k,v in mapping.items() if v is not None}
    df_renamed = df.rename(columns=rename_dict)
    # For any expected headers missing, add empty column
    for ex in EXPECTED:
        if ex not in df_renamed.columns:
            df_renamed[ex] = ""
    # Reorder to expected order (plus extras at end)
    ordered = [c for c in EXPECTED if c in df_renamed.columns]
    extras = [c for c in df_renamed.columns if c not in ordered]
    df_final = df_renamed[ordered + extras]
    df_final.to_csv(OUT, index=False)
    print(f"\nWrote fixed CSV to: {OUT}")
    print("Please open the fixed CSV, verify a few rows, then run the dry-run again:")
    print(f"  python auto_submit_gform.py --csv {OUT} --dry-run")

if __name__ == '__main__':
    main()
