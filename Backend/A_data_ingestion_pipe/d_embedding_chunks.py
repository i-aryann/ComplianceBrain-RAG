import json
import os
from tqdm import tqdm
from dotenv import load_dotenv

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import time

# ==============================
# CONFIG
# ==============================

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chunks_with_metadata.jsonl")
COLLECTION_NAME = "regulatory_rag"
BATCH_SIZE = 8

# ==============================
# LOAD ENV VARIABLES
# ==============================

load_dotenv()


# ==============================
# LOAD EMBEDDING MODEL
# ==============================

model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
    api_key= os.getenv("NVIDIA_API_KEY"),
    truncate="NONE"
)

# ==============================
# AUTO DETECT VECTOR DIMENSION
# ==============================

test_vec = model.embed_query("dimension test")
VECTOR_DIM = len(test_vec)

print(f"✅ Detected embedding dimension: {VECTOR_DIM}")

# ==============================
# CONNECT TO QDRANT
# ==============================

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=120
)

# Safe recreate collection
if client.collection_exists(COLLECTION_NAME):
    print("⚠️ Collection exists — deleting")
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=VECTOR_DIM,
        distance=Distance.COSINE
    )
)

print("✅ Collection created")

# ==============================
# EMBEDDING + INSERTION PIPELINE
# ==============================

batch_texts = []
batch_payloads = []
id_counter = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f, desc="Embedding Chunks"):

        chunk = json.loads(line)

        text = chunk.get("text", "").strip()

        # ⭐ Skip chunks with empty text — NVIDIA API rejects them
        if not text:
            print(f"⚠️  Skipping empty chunk from {chunk.get('source_file', '?')}")
            continue

        batch_texts.append(text)

        batch_payloads.append({
            "text": text,
            "regulation": chunk.get("regulation", "UNKNOWN"),
            "source_file": chunk.get("source_file", "UNKNOWN"),
            "page": chunk.get("page", -1),
            "clause_number": chunk.get("clause_number", "UNKNOWN"),
            "topic": chunk.get("topic", "GENERAL"),
            "regulation_type": chunk.get("regulation_type", "UNKNOWN"),
            "doc_id": chunk.get("doc_id", "UNKNOWN")
        })

        if len(batch_texts) == BATCH_SIZE:

            # Safety-net: replace any remaining empty strings (should never happen now)
            safe_texts = [t if t.strip() else " " for t in batch_texts]

            embeddings = model.embed_documents(safe_texts)

            points = [
                PointStruct(
                    id=id_counter + i,
                    vector=embeddings[i],
                    payload=batch_payloads[i]
                )
                for i in range(len(embeddings))
            ]

            for attempt in range(3):
                try:
                    client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=points
                    )
                    break
                except Exception as e:
                    print(f"⚠️ Upload failed, retry {attempt+1}/3")
                    time.sleep(3)

            id_counter += len(points)
            batch_texts = []
            batch_payloads = []

# Insert remaining batch
if batch_texts:

    safe_texts = [t if t.strip() else " " for t in batch_texts]
    embeddings = model.embed_documents(safe_texts)

    points = [
        PointStruct(
            id=id_counter + i,
            vector=embeddings[i],
            payload=batch_payloads[i]
        )
        for i in range(len(embeddings))
    ]

    for attempt in range(3):
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            break
        except Exception as e:
            print(f"⚠️ Final batch upload failed, retry {attempt+1}/3")
            time.sleep(3)

    id_counter += len(points)

print("🚀 Embedding + Vector DB Insertion Complete")