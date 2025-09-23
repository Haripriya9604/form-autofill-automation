# rename_entry_to_human.py
# Usage: python rename_entry_to_human.py
# Reads:  alumni_dataset_2017_2021_cleaned.csv (or the mapped entries file you have)
# Writes: alumni_dataset_2017_2021_cleaned_human.csv
import pandas as pd
from pathlib import Path

IN = "alumni_dataset_2017_2021_cleaned.csv"
OUT = "alumni_dataset_2017_2021_cleaned_human.csv"

# mapping we determined from your form earlier:
entry_to_human = {
    "Name": "entry.xxxxxxx",
    "Department": "entry.xxxxxxx",
    "Stream": "entry.xxxxxxx",
    "Year of Graduation": "entry.xxxxxxx",
    "Current Job Title and Employer": "entry.xxxxxxx",
    "Years Working": "entry.xxxxxxx",
    "University helped": "entry.xxxxxxx",
    "Areas to improve": "entry.xxxxxxx",
    "Education prepared me well": "entry.xxxxxxx",
    "Progressed in career": "entry.xxxxxxx",
    "Apply engineering principles": "entry.xxxxxxx",
    "Solve complex problems": "entry.732524708",
    "Consider broader societal issues": "entry.xxxxxxx",
    "Stay current with technologies": "entry.xxxxxxx",
    "Responsive to global issues": "entry.xxxxxxx",
    "Email": "emailAddress"
}

def main():
    p = Path(IN)
    if not p.exists():
        print(f"Input not found: {IN}. Make sure the mapped CSV is named exactly and is in this folder.")
        return
    df = pd.read_csv(p, dtype=str).fillna("")
    # Determine which of the entry keys exist
    rename_dict = {k:v for k,v in entry_to_human.items() if k in df.columns}
    if not rename_dict:
        print("No entry.* columns found to rename. Current columns:")
        print(list(df.columns))
        return
    df_renamed = df.rename(columns=rename_dict)
    # Reorder columns to expected human order, keep extras at the end
    expected_order = [
        "Email","Name","Department","Stream","Year of Graduation","Current Job Title and Employer",
        "Years Working","Education prepared me well","Progressed in career","Apply engineering principles",
        "Solve complex problems","Consider broader societal issues","Stay current with technologies",
        "Responsive to global issues","University helped","Areas to improve"
    ]
    ordered = [c for c in expected_order if c in df_renamed.columns]
    extras = [c for c in df_renamed.columns if c not in ordered]
    df_final = df_renamed[ordered + extras]
    df_final.to_csv(OUT, index=False)
    print(f"Wrote renamed CSV: {OUT}")
    print("Now run the dry-run with: python auto_submit_gform.py --csv " + OUT + " --dry-run")

if __name__ == "__main__":
    main()

