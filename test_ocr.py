import os
import pytesseract
from PIL import Image
import pandas as pd

# 🧠 Path to your dataset
dataset_path = r"D:\epics\medibridge_djongo\ml\data"

print("🔍 Starting OCR extraction...")

# List to store results
results = []

# Loop through all image files
for file in os.listdir(dataset_path):
    if file.endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(dataset_path, file)
        print(f"\n📄 Processing: {file}")

        try:
            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(Image.open(image_path))
            print("🩺 Extracted Text:")
            print(text)

            # Store filename and extracted text
            results.append({'filename': file, 'text': text})
        
        except Exception as e:
            print(f"⚠️ Error processing {file}: {e}")

# ✅ Save results to CSV
output_csv = os.path.join(dataset_path, 'ocr_results.csv')
df = pd.DataFrame(results)
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"\n✅ OCR extraction completed and saved to:\n{output_csv}")
