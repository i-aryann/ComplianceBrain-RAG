import json
import re
from tqdm import tqdm

INPUT_FILE = "chunks.jsonl"
OUTPUT_FILE = "chunks_with_metadata.jsonl"


def extract_clause_number(text):
    """
    Extract clause number like:
    5
    5.2
    5.2.3
    """

    match = re.search(r'\b\d+(?:\.\d+)+', text)

    if match:
        return match.group()

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

        new_chunks.append(chunk)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for ch in new_chunks:
        f.write(json.dumps(ch) + "\n")

print("✅ Metadata Enrichment Complete")