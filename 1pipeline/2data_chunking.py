import json
import re
import tiktoken
from tqdm import tqdm

INPUT_FILE = "raw_documents.jsonl"
OUTPUT_FILE = "chunks.jsonl"

CHUNK_SIZE = 500
OVERLAP = 100

enc = tiktoken.get_encoding("cl100k_base")


def split_clauses(text):
    """
    Split legal text using clause-number patterns like:
    1 , 1.2 , 5.2.3 etc.
    """

    if not text or not isinstance(text, str):
        return []

    # NON-capturing group regex (very important fix)
    pattern = r'\n?\s*(?=\d+(?:\.\d+)*\s+[A-Za-z])'

    parts = re.split(pattern, text)

    clauses = []

    for p in parts:
        if not p:
            continue

        if not isinstance(p, str):
            continue

        p = p.strip()

        if len(p) > 50:
            clauses.append(p)

    return clauses


chunks = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f):

        try:
            doc = json.loads(line)
        except:
            continue

        text = doc.get("text", None)

        if not text:
            continue

        clauses = split_clauses(text)

        for clause in clauses:

            tokens = enc.encode(clause)

            start = 0

            while start < len(tokens):

                end = start + CHUNK_SIZE

                chunk_tokens = tokens[start:end]

                chunk_text = enc.decode(chunk_tokens).strip()

                if len(chunk_text) < 40:
                    break

                chunk_entry = {
                    "text": chunk_text,
                    "regulation": doc.get("regulation", "UNKNOWN"),
                    "source_file": doc.get("source_file", "UNKNOWN"),
                    "page": doc.get("page", -1)
                }

                chunks.append(chunk_entry)

                start += CHUNK_SIZE - OVERLAP


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ch in chunks:
        f.write(json.dumps(ch) + "\n")

print(f"✅ Chunking Complete — Total chunks created: {len(chunks)}")