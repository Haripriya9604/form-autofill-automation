# retry_failed.py
import sys, os, time, random, csv, requests, pandas as pd

FORM_URL = "https://docs.google.com/forms/d/e/<PUBLIC ID>/formResponse"

def main():
    if len(sys.argv) < 2:
        print("Usage: python retry_failed.py <failed_chunk.csv>")
        sys.exit(1)

    infile = sys.argv[1]
    if not os.path.exists(infile):
        print("File not found:", infile)
        sys.exit(1)

    df = pd.read_csv(infile, dtype=str).fillna("")
    fname = os.path.basename(infile).replace(".csv", "")
    log_path = os.path.join("logs", f"retry_{fname}.csv")
    os.makedirs("logs", exist_ok=True)

    print(f"[{fname}] Retrying {len(df)} failed rows...")
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
                    timeout=50,
                )
                ok = 200 <= r.status_code < 400
                status = r.status_code
            except Exception as e:
                ok = False
                status = str(e)

            ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            writer.writerow([ts, idx, name, email, ok, status])
            lf.flush()

            print(f"[{fname}] Row {idx} -> {name} -> success={ok} status={status}")
            time.sleep(10 + random.random() * 1.0)  # longer delay

    print(f"[{fname}] Retry complete. Log saved to {log_path}")

if __name__ == "__main__":
    main()

