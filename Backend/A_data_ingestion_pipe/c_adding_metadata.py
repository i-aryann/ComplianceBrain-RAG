import json
import re
import os
from tqdm import tqdm

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE  = os.path.join(_BACKEND_DIR, "chunks.jsonl")
OUTPUT_FILE = os.path.join(_BACKEND_DIR, "chunks_with_metadata.jsonl")


def extract_clause_number(text):
    """
    Extract clause/section number from regulatory text.
    Handles patterns like:
      5.2.3  →  multi-level decimal
      5.2    →  two-level decimal
      5.     →  single numbered clause
      (1)    →  parenthesised number
      Section 4  →  section keyword
      Chapter 3  →  chapter keyword
    """

    # Priority 1: multi-level decimal  e.g. 5.2.3 or 5.2
    match = re.search(r'\b(\d+(?:\.\d+){1,})', text)
    if match:
        return match.group(1)

    # Priority 2: Section / Chapter keyword  e.g. "Section 4" or "CHAPTER 12"
    match = re.search(r'(?:section|chapter|clause|article|para(?:graph)?)\s+(\d+(?:\.\d+)*)',
                      text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Priority 3: parenthesised number  e.g. (1) or (iv)
    match = re.search(r'^\s*\((\d+|[ivxlcdm]+)\)', text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1)

    # Priority 4: standalone numbered item at line start  e.g. "4. Some rule"
    match = re.search(r'^\s*(\d{1,3})\.', text, re.MULTILINE)
    if match:
        return match.group(1)

    return "UNKNOWN"


def detect_topic(text):
    """
    Detect legal topic based on keywords
    """

    topic_keywords = {
        "KYC": ["kyc", "customer", "identity", "due diligence"],
        "AML": ["money laundering", "aml", "suspicious", "transaction monitoring"],
        "LENDING": ["loan", "credit", "lending", "borrower"],
        "GOVERNANCE": ["board", "director", "governance", "audit"],
        "CYBERSECURITY": ["cyber", "it risk", "data security"],
        "CAPITAL": ["capital adequacy", "risk weighted", "tier"],
        "LIQUIDITY": ["liquidity", "funding ratio", "lcr"]
    }

    text_lower = text.lower()

    for topic, words in topic_keywords.items():
        for w in words:
            if w in text_lower:
                return topic

    return "GENERAL"


def detect_regulation_type(file_name):
    """
    Tag regulation domain using file name
    """

    name = file_name.lower()

    if "kyc" in name:
        return "KYC"
    elif "nbfc" in name:
        return "NBFC"
    elif "cyber" in name:
        return "IT"
    elif "lending" in name:
        return "LENDING"
    elif "basel" in name:
        return "BASEL"
    else:
        return "GENERAL"


new_chunks = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f):

        chunk = json.loads(line)

        text = chunk["text"]

        clause_number = extract_clause_number(text)

        topic = detect_topic(text)

        regulation_type = detect_regulation_type(chunk["source_file"])

        chunk["clause_number"] = clause_number
        chunk["topic"] = topic
        chunk["regulation_type"] = regulation_type
        # Friendly doc_id used in citations
        src = chunk.get('source_file', 'UNKNOWN')
        reg = chunk.get('regulation', regulation_type)
        chunk["doc_id"] = f"{reg} | {src} | Clause {clause_number}"

        new_chunks.append(chunk)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ch in new_chunks:
        f.write(json.dumps(ch) + "\n")

print("✅ Metadata Enrichment Complete")