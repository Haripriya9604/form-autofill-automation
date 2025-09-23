# fetch_form_info.py
# Usage: python fetch_form_info.py "<viewform_url>"
import sys, requests, re

if len(sys.argv) < 2:
    print("Usage: python fetch_form_info.py \"https://.../viewform\"")
    sys.exit(1)

url = sys.argv[1]

print("Fetching:", url)
r = requests.get(url, timeout=30)
print("GET status:", r.status_code)
html = r.text

# find /formResponse occurrences (paths)
form_responses = set()
form_responses.update(re.findall(r'/forms/d/e/[^"\']+/formResponse', html))
form_responses.update(re.findall(r'/formResponse[^"\']*', html))

fr = sorted(form_responses)
print("\nformResponse occurrences found:", len(fr))
for x in fr[:40]:
    print("  ->", x)

# find entry ids
entry_ids = sorted(set(re.findall(r'name="(entry\.\d+)"', html)))
print("\nFound entry ids count:", len(entry_ids))
if entry_ids:
    print(", ".join(entry_ids[:120]))
else:
    print("(no entry.* ids found in HTML)")

# show small HTML snippet for eyeballing near first "entry."
m = re.search(r'(entry\.\d+)', html)
if m:
    idx = m.start()
    start = max(0, idx - 400)
    snippet = html[start: start + 1200].replace("\n", " ")
    print("\n--- HTML snippet around first entry id ---")
    print(snippet[:1200])
else:
    print("\n(no entry.* snippet found)")
