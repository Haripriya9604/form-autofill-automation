#!/usr/bin/env python3
"""
auto_submit_gform.py
Generalized bulk submitter for Google Forms.

Behavior:
- Loads mapping & form URL from local config.json (if present).
- If config.json missing, uses placeholder mapping (safe to publish).
- Supports --dry-run, --test-rows, --resume, delay/jitter and logging.

Quick:
  python auto_submit_gform.py --csv sample_input.csv --dry-run
  python auto_submit_gform.py --csv sample_input.csv --form-url "https://docs.google.com/forms/d/e/REAL_ID/formResponse" --test-rows 3
"""
import argparse, time, random, csv, logging, json
from pathlib import Path
from datetime import datetime
import pandas as pd
import requests
from tqdm import tqdm

# Default placeholders (safe for public repo)
PLACEHOLDER_FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"
PLACEHOLDER_MAPPING = {
    "Name": "entry.YOUR_ENTRY_ID_HERE",
    "Department": "entry.YOUR_ENTRY_ID_HERE",
    "Stream": "entry.YOUR_ENTRY_ID_HERE",
    "Year of Graduation": "entry.YOUR_ENTRY_ID_HERE",
    "Current Job Title and Employer": "entry.YOUR_ENTRY_ID_HERE",
    "Years Working": "entry.YOUR_ENTRY_ID_HERE",
    "University helped": "entry.YOUR_ENTRY_ID_HERE",
    "Areas to improve": "entry.YOUR_ENTRY_ID_HERE",
    "Education prepared me well": "entry.YOUR_ENTRY_ID_HERE",
    "Progressed in career": "entry.YOUR_ENTRY_ID_HERE",
    "Apply engineering principles": "entry.YOUR_ENTRY_ID_HERE",
    "Solve complex problems": "entry.YOUR_ENTRY_ID_HERE",
    "Consider broader societal issues": "entry.YOUR_ENTRY_ID_HERE",
    "Stay current with technologies": "entry.YOUR_ENTRY_ID_HERE",
    "Responsive to global issues": "entry.YOUR_ENTRY_ID_HERE",
    "Email": "emailAddress"
}
DEFAULT_LOG = "submissions_log.csv"

# -------------------------
def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

def load_config(path="config.json"):
    p = Path(path)
    if not p.exists():
        return {"form_url": PLACEHOLDER_FORM_URL, "mapping": PLACEHOLDER_MAPPING}
    try:
        with p.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
        form_url = cfg.get("form_url", PLACEHOLDER_FORM_URL)
        mapping = cfg.get("mapping", PLACEHOLDER_MAPPING)
        return {"form_url": form_url, "mapping": mapping}
    except Exception as e:
        logging.warning("Failed loading config.json: %s", e)
        return {"form_url": PLACEHOLDER_FORM_URL, "mapping": PLACEHOLDER_MAPPING}

def validate_headers(df, required_keys):
    missing = [k for k in required_keys if k not in df.columns]
    return missing

def build_payload_from_row(row, mapping):
    payload = {}
    for human_col, entry_name in mapping.items():
        val = row.get(human_col, "")
        if pd.isna(val):
            val = ""
        payload[entry_name] = str(val)
    return payload

def post_with_retries(session, url, payload, max_retries=5, backoff_base=1.8, timeout=30):
    attempt = 0
    while attempt <= max_retries:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Referer": url.replace("/formResponse", "/viewform")
            }
            r = session.post(url, data=payload, headers=headers, timeout=timeout, allow_redirects=False)
            status = r.status_code
            if 200 <= status < 400:
                return True, status, r.text[:200]
            else:
                logging.warning("Bad status %s (attempt %d).", status, attempt)
        except Exception as e:
            logging.warning("Exception during POST (attempt %d): %s", attempt, e)
        attempt += 1
        time.sleep((backoff_base ** attempt) + random.random())
    return False, None, None

def write_log_row(log_path, row_index, name, email, success, status, preview):
    file_exists = Path(log_path).exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp","row_index","Name","Email","success","status","payload_preview"])
        writer.writerow([datetime.utcnow().isoformat(), row_index, name, email, success, status, preview])

def read_resume_index(log_path):
    p = Path(log_path)
    if not p.exists():
        return 0
    df = pd.read_csv(p)
    if "success" not in df.columns or "row_index" not in df.columns:
        return 0
    success_rows = df[df["success"] == True] if df["success"].dtype == bool else df[df["success"].astype(str).str.lower() == "true"]
    if success_rows.empty:
        return 0
    last = int(success_rows["row_index"].max())
    return last + 1

def main():
    setup_logger()
    parser = argparse.ArgumentParser(description="General bulk submitter for Google Forms")
    parser.add_argument("--csv", required=True, help="Path to CSV input")
    parser.add_argument("--form-url", default=None, help="Optional override formResponse URL")
    parser.add_argument("--config", default="config.json", help="Local config.json to load mapping and form url")
    parser.add_argument("--delay", type=float, default=1.5, help="Base delay between submissions (seconds)")
    parser.add_argument("--jitter", type=float, default=0.6, help="Random jitter seconds")
    parser.add_argument("--max-retries", type=int, default=5, help="Max retries per row")
    parser.add_argument("--test-rows", type=int, default=0, help="If >0, only POST this many rows")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads instead of posting")
    parser.add_argument("--resume", action="store_true", help="Resume from log file")
    parser.add_argument("--log", default=DEFAULT_LOG, help="Log file path")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        logging.error("CSV not found: %s", csv_path)
        return

    cfg = load_config(args.config)
    form_url = args.form_url if args.form_url else cfg["form_url"]
    mapping = cfg["mapping"]

    if "YOUR_FORM_ID" in form_url or "YOUR_ENTRY_ID" in str(mapping):
        logging.warning("CONFIG contains placeholders. Replace config.json values with real IDs before live run, or pass --form-url.")

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    logging.info("Loaded CSV rows: %d", len(df))

    missing = validate_headers(df, list(mapping.keys()))
    if missing:
        logging.error("Missing required columns in CSV: %s", ", ".join(missing))
        logging.info("Required columns: %s", ", ".join(mapping.keys()))
        return

    start_index = 0
    if args.resume:
        start_index = read_resume_index(args.log)
        logging.info("Resuming from row index %d", start_index)

    session = requests.Session()
    total = len(df)
    indices = range(start_index, total)
    if args.test_rows and args.test_rows > 0:
        indices = range(start_index, min(start_index + args.test_rows, total))

    if args.dry_run:
        logging.info("DRY RUN - previewing first 5 payloads")
        for i in list(indices)[:5]:
            payload = build_payload_from_row(df.iloc[i], mapping)
            print(f"Row {i} preview:", {k:v[:120] for k,v in payload.items()})
        return

    pbar = tqdm(indices, desc="Submitting")
    for i in pbar:
        row = df.iloc[i]
        payload = build_payload_from_row(row, mapping)
        preview = str({k:(v[:140] if isinstance(v,str) else str(v)) for k,v in payload.items()})
        name = row.get("Name","")
        email = row.get("Email","")
        ok, status, _ = post_with_retries(session, form_url, payload, max_retries=args.max_retries)
        write_log_row(args.log, i, name, email, ok, status, preview)
        pbar.set_postfix({"row": i, "name": name, "ok": ok, "status": status})
        time.sleep(args.delay + random.random() * args.jitter)

    logging.info("Done. Check log file: %s", args.log)

if __name__ == "__main__":
    main()
