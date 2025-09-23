import pandas as pd

# Load the first chunk (50 rows)
df = pd.read_csv("mapped/chunks/chunk_1.csv", dtype=str).fillna("")

# Save only the first row for testing
df.head(1).to_csv("mapped/chunks/chunk_1_testsingle.csv", index=False)

print("WROTE mapped/chunks/chunk_1_testsingle.csv")
