#!/usr/bin/env python3
"""
map_and_chunk_alumini.py

- Reads an input Excel (.xlsx) or CSV file with human headers (Name, Department, Stream, ...)
- Maps human headers to entry.* IDs required by the Google Form
- Canonicalizes Likert answers to exact options
- Ensures emailAddress exists (generates unique emails from Name if missing)
- Computes Years Working = max(0, 2025 - YearOfGraduation) when Years Working missing/empty
- Writes mapped CSV to mapped/Alumini_mapped_for_form.csv
- Splits into chunks of 50 rows into mapped/chunks/chunk_1.csv, ...
- Prints a small dry-run preview

Usage:
    python map_and_chunk_alumini.py --input "input\\Alumini_2019_2023_cleaned_dataset.xlsx"
"""

import argparse
import os
from pathlib import Path
import pandas as pd
import re
import random
from collections import defaultdict

random.seed(42)

# ---- mapping human -> entry IDs (same mapping we used earlier) ----
FIELD_TO_ENTRY = {
    "Name": "entry.24240767",
    "Department": "entry.283251996",
    "Stream": "entry.296483464",
    "Year of Graduation": "entry.494363075",
    "Current Job Title and Employer": "entry.756242332",
    "Years Working": "entry.1536199188",
    "University helped": "entry.816875948",
    "Areas to improve": "entry.202739707",
    "Education prepared me well": "entry.1739490987",
    "Progressed in career": "entry.143592356",
    "Apply engineering principles": "entry.1333872725",
    "Solve complex problems": "entry.732524708",
    "Consider broader societal issues": "entry.910737851",
    "Stay current with technologies": "entry.288733793",
    "Responsive to global issues": "entry.1611035480",
    "Email": "emailAddress"
}

LIKERT_HEADERS = {
    "Education prepared me well",
    "Progressed in career",
    "Apply engineering principles",
    "Solve complex problems",
    "Consider broader societal issues",
    "Stay current with technologies",
    "Responsive to global issues",
}

LIKERT_CANON = {
    "strongly": "Strongly agree",
    "strongly agree": "Strongly agree",
    "agree": "Agree",
    "neutral": "Neutral",
    "neither": "Neutral",
    "disagree": "Disagree",
    "strongly disagree": "Strongly disagree",
}

DEFAULT_UNI = "Helpful faculty and curriculum; strong project guidance."
DEFAULT_AREA = "Increase industry collaborations and company internships."

# ---- helpers ----
def canonical_likert(v):
    s = str(v).strip()
    if not s:
        return ""
    s_low = s.lower()
    for k, out in LIKERT_CANON.items():
        if s_low.startswith(k):
            return out
    # fallback: if contains agree/neutral/disagree words
    if "strong" in s_low and "agree" in s_low:
        return "Strongly agree"
    if "agree" in s_low:
        return "Agree"
    if "neutral" in s_low or "neither" in s_low:
        return "Neutral"
    if "disagree" in s_low:
        return "Disagree"
    return s  # leave as-is if unknown

def make_email_from_name(name, used_set, domains):
    # create local part: first.last (keep punctuation removed). Add 2-digit random sometimes.
    parts = re.findall(r"[a-z0-9]+", name.lower())
    if not parts:
        local = "user"
    elif len(parts) == 1:
        local = parts[0]
    else:
        local = parts[0] + "." + parts[-1]
    add_num = random.choice([False, False, True])
    if add_num:
        local = f"{local}{random.randint(1,99)}"
    domain = random.choice(domains)
    candidate = f"{local}@{domain}"
    suffix = 0
    while candidate in used_set:
        suffix += 1
        candidate = f"{local}{suffix}@{domain}"
    used_set.add(candidate)
    return candidate

def safe_int_year(y):
    try:
        m = re.search(r"(20\d{2})", str(y))
        if m:
            return int(m.group(1))
        return int(str(y))
    except Exception:
        return None

def ensure_dir(p:Path):
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

# ---- main function ----
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", required=True, help="Input path (.csv or .xlsx)")
    p.add_argument("--chunksize", type=int, default=50, help="Rows per chunk")
    p.add_argument("--out-mapped", default="mapped/Alumini_mapped_for_form.csv", help="Mapped CSV output path")
    args = p.parse_args()

    IN = Path(args.input)
    OUT = Path(args.out_mapped)
    CHUNK_DIR = OUT.parent / "chunks"
    ensure_dir(OUT.parent)
    ensure_dir(CHUNK_DIR)

    if not IN.exists():
        print("Input file not found:", IN)
        return

    # read input (csv or xlsx)
    if IN.suffix.lower() in [".xls", ".xlsx"]:
        df = pd.read_excel(IN, dtype=str).fillna("")
    else:
        df = pd.read_csv(IN, dtype=str).fillna("")

    nrows = len(df)
    print(f"Loaded {nrows} rows from {IN}")

    # normalize column names (strip)
    df.columns = [c.strip() for c in df.columns]

    # Ensure Email exists or generate later
    # pick email-like column if present
    email_col = None
    for c in df.columns:
        if c.lower() in ("email","email address","e-mail","emailaddress","email_address"):
            email_col = c
            break
    # Prepare email list (unique)
    used = set()
    domains = ["gmail.com","yahoo.com","outlook.com","hotmail.com","protonmail.com"]
    emails = []
    if email_col:
        for i, val in enumerate(df[email_col].astype(str).fillna("")):
            v = val.strip().lower()
            if v and "@" in v:
                # ensure unique
                candidate = v
                base, dom = candidate.split("@",1)
                suf = 0
                while candidate in used:
                    suf += 1
                    candidate = f"{base}{suf}@{dom}"
                used.add(candidate)
                emails.append(candidate)
            else:
                emails.append(None)
    else:
        emails = [None]*nrows

    # generate emails for rows missing
    for i in range(nrows):
        if emails[i] is None or emails[i] == "":
            name = df.iloc[i].get("Name", "") if "Name" in df.columns else ""
            candidate = make_email_from_name(name or f"user{i+1}", used, domains)
            emails[i] = candidate
    # ensure final unique
    # build mapped DataFrame
    mapped = pd.DataFrame(index=df.index)

    # Fill Years Working from Year of Graduation if Years Working blank
    for idx in df.index:
        if "Years Working" not in df.columns or str(df.loc[idx].get("Years Working","")).strip() == "":
            yg = df.loc[idx].get("Year of Graduation","")
            yy = safe_int_year(yg)
            if yy:
                years_working = max(0, 2025 - yy)
            else:
                years_working = 2  # default fallback
            df.at[idx, "Years Working"] = str(years_working)

    # Fill University helped / Areas to improve defaults if missing
    if "University helped" not in df.columns:
        df["University helped"] = DEFAULT_UNI
    else:
        df["University helped"] = df["University helped"].astype(str).fillna("")
        df["University helped"] = df["University helped"].apply(lambda x: x if x.strip() else DEFAULT_UNI)
    if "Areas to improve" not in df.columns:
        df["Areas to improve"] = DEFAULT_AREA
    else:
        df["Areas to improve"] = df["Areas to improve"].astype(str).fillna("")
        df["Areas to improve"] = df["Areas to improve"].apply(lambda x: x if x.strip() else DEFAULT_AREA)

    # Canonicalize likert columns if present
    for h in LIKERT_HEADERS:
        if h in df.columns:
            df[h] = df[h].apply(canonical_likert)

    # Now map human -> entry
    for human, entry in FIELD_TO_ENTRY.items():
        if human == "Email":
            mapped[entry] = pd.Series(emails)
            continue
        if human in df.columns:
            mapped[entry] = df[human].astype(str).fillna("")
        else:
            # if missing human header, create empty column
            mapped[entry] = pd.Series([""] * nrows)

    # final sanity: ensure emailAddress column exists
    if "emailAddress" not in mapped.columns:
        # fallback, set from emails variable
        mapped["emailAddress"] = pd.Series(emails)

    # write mapped CSV
    mapped.to_csv(OUT, index=False, encoding="utf-8")
    print("WROTE mapped CSV:", OUT, "Rows:", len(mapped))

    # chunk into CHUNK_DIR
    chunk_size = int(args.chunksize)
    num_chunks = 0
    for i in range(0, len(mapped), chunk_size):
        num_chunks += 1
        chunk = mapped.iloc[i:i+chunk_size]
        outp = CHUNK_DIR / f"chunk_{num_chunks}.csv"
        chunk.to_csv(outp, index=False, encoding="utf-8")
    print(f"WROTE {num_chunks} chunk files to {CHUNK_DIR} (chunk_size={chunk_size})")

    # Dry-run preview: print first 3 payloads
    print("\nDRY RUN PREVIEW (first 3 payloads):")
    for i, row in mapped.head(3).iterrows():
        # show a concise dict
        d = row.to_dict()
        # hide huge noise - show first 6 keys
        preview_keys = list(d.keys())[:8]
        preview = {k: d[k] for k in preview_keys}
        print(f"Row {i} preview:", preview)

if __name__ == "__main__":
    main()
