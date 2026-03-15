import json
import os
from tqdm import tqdm
from dotenv import load_dotenv

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# ==============================
# CONFIG
# ==============================

INPUT_FILE = "chunks_with_metadata.jsonl"
COLLECTION_NAME = "regulatory_rag"
BATCH_SIZE = 64

# ==============================
# LOAD ENV VARIABLES
# ==============================

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise ValueError("❌ NVIDIA_API_KEY not found in .env")

# ==============================
# LOAD EMBEDDING MODEL
# ==============================

model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
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

client = QdrantClient(host="localhost", port=6333)

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

        batch_texts.append(chunk["text"])

        batch_payloads.append({
            "text": chunk["text"],
            "regulation": chunk["regulation"],
            "source_file": chunk["source_file"],
            "page": chunk["page"],
            "clause_number": chunk["clause_number"],
            "topic": chunk["topic"],
            "regulation_type": chunk["regulation_type"]
        })

        if len(batch_texts) == BATCH_SIZE:

            embeddings = model.embed_documents(batch_texts)

            points = [
                PointStruct(
                    id=id_counter + i,
                    vector=embeddings[i],
                    payload=batch_payloads[i]
                )
                for i in range(len(embeddings))
            ]

            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )

            id_counter += len(points)
            batch_texts = []
            batch_payloads = []

# Insert remaining
if batch_texts:

    embeddings = model.embed_documents(batch_texts)

    points = [
        PointStruct(
            id=id_counter + i,
            vector=embeddings[i],
            payload=batch_payloads[i]
        )
        for i in range(len(embeddings))
    ]

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

print("🚀 Embedding + Vector DB Insertion Complete")