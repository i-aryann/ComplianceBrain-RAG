import fitz  # PyMuPDF
import os
import json
from tqdm import tqdm

# Resolve paths relative to Backend/ (one level above this script)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR    = os.path.join(_BACKEND_DIR, "Data")
OUTPUT_FILE = os.path.join(_BACKEND_DIR, "raw_documents.jsonl")

def detect_regulation(folder_name):
    return folder_name.upper()

all_docs = []

for folder in os.listdir(DATA_DIR):
    folder_path = os.path.join(DATA_DIR, folder)

    if not os.path.isdir(folder_path):
        continue

    regulation = detect_regulation(folder)

    for file in tqdm(os.listdir(folder_path)):
        if not file.endswith(".pdf"):
            continue

        file_path = os.path.join(folder_path, file)

        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            text = text.replace("\n", " ").strip()

            if len(text) < 50:
                continue

            entry = {
                "text": text,
                "regulation": regulation,
                "source_file": file,
                "page": page_num + 1
            }

            all_docs.append(entry)

with open(OUTPUT_FILE, "w") as f:
    for doc in all_docs:
        f.write(json.dumps(doc) + "\n")

print("Parsing Complete")