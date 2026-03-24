import json
import re
import tiktoken
from tqdm import tqdm
from collections import defaultdict

INPUT_FILE = "raw_documents.jsonl"
OUTPUT_FILE = "chunks.jsonl"

CHUNK_SIZE = 400
OVERLAP = 80

enc = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------
# STEP-1 → GROUP FULL DOCUMENT TEXT (not page wise)
# ---------------------------------------------------
docs = defaultdict(lambda: {
    "text_parts": [],
    "regulation": None,
    "source_file": None
})

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            d = json.loads(line)
        except:
            continue

        key = d.get("source_file")

        docs[key]["text_parts"].append(d.get("text", ""))
        docs[key]["regulation"] = d.get("regulation")
        docs[key]["source_file"] = key


# ---------------------------------------------------
# STEP-2 → ROBUST CLAUSE SPLITTER
# ---------------------------------------------------
def split_clauses(text):

    pattern = r'(?=\n?\s*(?:\(\d+\)|\d+\.\d+|\d+\.|\([ivx]+\)|[A-Z]\.|CHAPTER|Chapter|SECTION|Section))'

    parts = re.split(pattern, text)

    clauses = []

    for p in parts:
        p = p.strip()

        if len(p) > 150:
            clauses.append(p)

    return clauses


# ---------------------------------------------------
# STEP-3 + STEP-4 → MERGE CLAUSES + OVERLAP
# ---------------------------------------------------
def build_chunks(clauses):

    chunks = []
    current_chunk = ""

    for clause in clauses:

        curr_tokens = len(enc.encode(current_chunk))
        clause_tokens = len(enc.encode(clause))

        if curr_tokens + clause_tokens < CHUNK_SIZE:

            current_chunk += " " + clause

        else:

            chunks.append(current_chunk.strip())

            # overlap
            words = current_chunk.split()
            overlap_text = " ".join(words[-OVERLAP:])

            current_chunk = overlap_text + " " + clause

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# ---------------------------------------------------
# FINAL CHUNK CREATION
# ---------------------------------------------------
all_chunks = []

for doc_key in tqdm(docs.keys()):

    full_text = "\n".join(docs[doc_key]["text_parts"])

    clauses = split_clauses(full_text)

    merged_chunks = build_chunks(clauses)

    for ch in merged_chunks:

        entry = {
            "text": ch,
            "regulation": docs[doc_key]["regulation"],
            "source_file": docs[doc_key]["source_file"]
        }

        all_chunks.append(entry)


# ---------------------------------------------------
# SAVE
# ---------------------------------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ch in all_chunks:
        f.write(json.dumps(ch) + "\n")

print("\n✅ FINAL CHUNKING COMPLETE")
print("Total Chunks:", len(all_chunks))