# verify_submissions.py
# Usage: python verify_submissions.py
# Produces: verification_report.txt and failed_rows.csv (if any)
import csv, ast, sys
from pathlib import Path
import pandas as pd

LOG = "submissions_log.csv"
SRC = "alumni_dataset_2017_2021_cleaned_human_fixed.csv"
REPORT = "verification_report.txt"
FAILED_ROWS = "failed_rows.csv"

def load_log():
    p = Path(LOG)
    if not p.exists():
        print("Log file not found:", LOG); sys.exit(1)
    df = pd.read_csv(p, dtype=str).fillna("")
    # normalize types
    df['row_index'] = df['row_index'].astype(int)
    df['success'] = df['success'].astype(str)
    return df

def load_src():
    p = Path(SRC)
    if not p.exists():
        print("Source CSV not found:", SRC); sys.exit(1)
    df = pd.read_csv(p, dtype=str).fillna("")
    return df

def parse_preview_field(preview):
    # preview is like a string representation of a dict: "{'entry.242...': 'Name', ...}"
    try:
        d = ast.literal_eval(preview)
        if isinstance(d, dict):
            return {k:str(v) for k,v in d.items()}
    except Exception:
        pass
    return None

def main():
    log = load_log()
    src = load_src()
    total_rows = len(src)
    # summary
    successes = log[log['success'].str.lower() == 'true']
    failures = log[log['success'].str.lower() != 'true']
    report_lines = []
    report_lines.append(f"Local source rows: {total_rows}")
    report_lines.append(f"Total log entries: {len(log)}")
    report_lines.append(f"Successful submissions recorded: {len(successes)}")
    report_lines.append(f"Failed submissions recorded: {len(failures)}")
    # check for duplicate emails in source
    if 'Email' in src.columns:
        dup_emails = src['Email'][src['Email'].duplicated()].unique().tolist()
        report_lines.append(f"Duplicate emails in source CSV: {len(dup_emails)} -> {dup_emails[:10]}")
    else:
        report_lines.append("Source CSV has no 'Email' column to check duplicates.")

    # find which source rows were not submitted successfully
    submitted_row_indices = sorted(successes['row_index'].unique().tolist())
    missing_indices = [i for i in range(total_rows) if i not in submitted_row_indices]
    report_lines.append(f"Rows missing from successful submissions (by index): {missing_indices}")

    # verify payload values match source values (for mapped entry.* keys)
    # Build a small mapping of entry.* -> friendly name based on FIELD_MAPPING used earlier
    field_map = {
        "entry.24240767":"Name","entry.283251996":"Department","entry.296483464":"Stream",
        "entry.494363075":"Year of Graduation","entry.756242332":"Current Job Title and Employer",
        "entry.1536199188":"Years Working","entry.816875948":"University helped","entry.202739707":"Areas to improve",
        "entry.1739490987":"Education prepared me well","entry.143592356":"Progressed in career",
        "entry.1333872725":"Apply engineering principles","entry.732524708":"Solve complex problems",
        "entry.910737851":"Consider broader societal issues","entry.288733793":"Stay current with technologies",
        "entry.1611035480":"Responsive to global issues","emailAddress":"Email"
    }

    mismatches = []
    for _, row in successes.iterrows():
        idx = int(row['row_index'])
        if idx < 0 or idx >= total_rows:
            mismatches.append((idx, "row_index_out_of_range"))
            continue
        preview = row.get('payload_preview','')
        parsed = parse_preview_field(preview)
        if parsed is None:
            mismatches.append((idx, "could_not_parse_payload_preview"))
            continue
        src_row = src.iloc[idx].to_dict()
        # compare each mapped field
        for entry_key, friendly in field_map.items():
            src_val = str(src_row.get(friendly,"") or "").strip()
            payload_val = str(parsed.get(entry_key,"") or "").strip()
            # For some fields (open text) small whitespace differences OK; do exact compare for Likert/short values
            if src_val != payload_val:
                mismatches.append((idx, friendly, src_val, payload_val))

    report_lines.append(f"Payload vs source mismatches count: {len(mismatches)}")
    # write detailed mismatches to report
    with open(REPORT,"w",encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n\n")
        f.write("Detailed mismatches (first 200):\n")
        for m in mismatches[:200]:
            f.write(str(m) + "\n")
    print("Wrote verification summary to", REPORT)

    # create failed_rows.csv to retry any failures or missing rows
    failed_indices = sorted(set(missing_indices) | set(failures['row_index'].astype(int).tolist()))
    if failed_indices:
        df_failed = src.iloc[failed_indices]
        df_failed.to_csv(FAILED_ROWS,index=False)
        print(f"Wrote {len(failed_indices)} failed rows to {FAILED_ROWS}")
    else:
        print("No failed rows; nothing written to", FAILED_ROWS)

if __name__ == "__main__":
    main()
