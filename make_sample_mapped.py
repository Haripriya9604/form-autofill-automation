import pandas as pd

# Placeholder mapping
FIELD_TO_ENTRY = {
    "Name": "entry.111111111",
    "Department": "entry.222222222",
    "Stream": "entry.333333333",
    "Year of Graduation": "entry.444444444",
    "Current Job Title and Employer": "entry.555555555",
    "Years Working": "entry.666666666",
    "University helped": "entry.777777777",
    "Areas to improve": "entry.888888888",
    "Education prepared me well": "entry.999999999",
    "Progressed in career": "entry.1010101010",
    "Apply engineering principles": "entry.1112131415",
    "Solve complex problems": "entry.1213141516",
    "Consider broader societal issues": "entry.1314151617",
    "Stay current with technologies": "entry.1415161718",
    "Responsive to global issues": "entry.1516171819",
    "Email": "emailAddress"
}

df = pd.read_csv("sample_input.csv", dtype=str)

# Rename columns
df_mapped = df.rename(columns=FIELD_TO_ENTRY)

# Save
df_mapped.to_csv("sample_mapped_for_form.csv", index=False, encoding="utf-8")
print("✅ Wrote sample_mapped_for_form.csv with placeholder entry IDs")
