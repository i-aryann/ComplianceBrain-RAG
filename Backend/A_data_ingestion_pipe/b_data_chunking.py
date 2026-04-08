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
    "text_parts": [],   # list of (page_num, text)
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

        docs[key]["text_parts"].append((d.get("page", 1), d.get("text", "")))
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

    # Build a list of (page, text) while keeping text in order
    page_text_pairs = docs[doc_key]["text_parts"]

    # Build a simple page-lookup: character offset → page number
    # We concatenate texts with a sentinel so we can map chunk text back to pages
    page_map = []   # list of (cumulative_char_end, page_num)
    combined_text = ""
    for page_num, text in page_text_pairs:
        combined_text += text + "\n"
        page_map.append((len(combined_text), page_num))

    clauses = split_clauses(combined_text)

    merged_chunks = build_chunks(clauses)

    # Walk through merged_chunks and assign the best page from page_map
    cursor = 0  # rough character position tracker in combined_text
    for ch in merged_chunks:

        # Find page whose text first appears in the combined text near cursor
        chunk_start = combined_text.find(ch[:50], cursor)  # anchor on first 50 chars
        if chunk_start == -1:
            chunk_start = cursor
        cursor = chunk_start

        # Pick the page whose cumulative end is *after* this position
        page_num = 1
        for end_pos, pg in page_map:
            if chunk_start < end_pos:
                page_num = pg
                break

        entry = {
            "text": ch,
            "regulation": docs[doc_key]["regulation"],
            "source_file": docs[doc_key]["source_file"],
            "page": page_num
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