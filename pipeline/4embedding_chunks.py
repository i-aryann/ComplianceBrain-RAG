import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

INPUT_FILE = "chunks_with_metadata.jsonl"
COLLECTION_NAME = "regulatory_rag"

# Load embedding model
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Create collection (run only once)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE
    )
)

points = []
id_counter = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f):

        chunk = json.loads(line)

        text = chunk["text"]

        embedding = model.encode(text).tolist()

        payload = {
            "text": text,
            "regulation": chunk["regulation"],
            "source_file": chunk["source_file"],
            "page": chunk["page"],
            "clause_number": chunk["clause_number"],
            "topic": chunk["topic"],
            "regulation_type": chunk["regulation_type"]
        }

        point = PointStruct(
            id=id_counter,
            vector=embedding,
            payload=payload
        )

        points.append(point)

        id_counter += 1

        # Batch insert every 64 points (important)
        if len(points) == 64:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            points = []

# Insert remaining points
if points:
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

print("✅ Embedding + Vector DB Insertion Complete")