# post_chunk_poster.py
import sys, os, time, random, csv, requests, pandas as pd

# === UPDATE FORM_URL if form changes ===
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe4EdZ51rEN7tShoRf5wcLijsZw0XkrSWSLLQ53-ksso4MGXg/formResponse"

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_chunk_poster.py <chunk_file.csv>")
        sys.exit(1)

    infile = sys.argv[1]
    if not os.path.exists(infile):
        print("File not found:", infile)
        sys.exit(1)

    df = pd.read_csv(infile, dtype=str).fillna("")
    chunk_name = os.path.basename(infile).replace(".csv", "")
    log_path = os.path.join("logs", f"submissions_{chunk_name}.csv")
    os.makedirs("logs", exist_ok=True)

    print(f"[{chunk_name}] Loaded {len(df)} rows from {infile}")
    s = requests.Session()

    with open(log_path, "w", newline="", encoding="utf-8") as lf:
        writer = csv.writer(lf)
        writer.writerow(["timestamp", "row_index", "name", "email", "success", "status"])

        for idx, row in df.iterrows():
            payload = row.to_dict()
            email = payload.get("emailAddress", "")
            name = payload.get("entry.24240767", "")

            try:
                r = s.post(
                    FORM_URL,
                    data=payload,
                    headers={"Referer": FORM_URL.replace("/formResponse", "/viewform")},
                    allow_redirects=False,
                    timeout=40,
                )
                ok = 200 <= r.status_code < 400
                status = r.status_code
            except Exception as e:
                ok = False
                status = str(e)

            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            writer.writerow([ts, idx, name, email, ok, status])
            lf.flush()

            print(f"[{chunk_name}] Row {idx} -> {name} -> success={ok} status={status}")
            time.sleep(6 + random.random() * 0.6)  # delay per row

    print(f"[{chunk_name}] Done. Log saved to {log_path}")

if __name__ == "__main__":
    main()
