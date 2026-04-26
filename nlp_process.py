import pandas as pd
import re
import json

# Read OCR results (update path if needed)
df = pd.read_csv(r"D:\epics\medibridge_djongo\ml\data\ocr_results.csv")


def clean_text(text):
    if pd.isna(text):
        return ""
    text = re.sub(r'\s+', ' ', str(text))  # remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9.,:/\-() ]', '', text)
    return text.strip()

def extract_info(text):
    text = clean_text(text)

    doctor = re.findall(r'Dr\.?\s+[A-Z][a-zA-Z. ]+', text)
    medicines = re.findall(r'(Tab|Cap|Syrup|Inj|Tablet|Capsule|Drops)[^.,\n]+', text)
    dosage = re.findall(r'\b(\d-\d-\d|BD|TDS|OD|HS)\b', text)
    expiry = re.findall(r'(0[1-9]|1[0-2])\/\d{2,4}', text)

    return {
        "doctor": doctor,
        "medicines": medicines,
        "dosage": dosage,
        "expiry": expiry
    }

# Process all rows
results = []
for _, row in df.iterrows():
    file_name = row.get("file") or row.get("filename") or "unknown"
    text = row.get("text") or ""
    info = extract_info(text)
    results.append({
        "file": file_name,
        "doctor": info["doctor"],
        "medicines": info["medicines"],
        "dosage": info["dosage"],
        "expiry": info["expiry"]
    })

# Save as JSON
with open("ml/data/nlp_results.json", "w") as f:
    json.dump(results, f, indent=4)

print("✅ NLP extraction complete — results saved at: ml/data/nlp_results.json")
