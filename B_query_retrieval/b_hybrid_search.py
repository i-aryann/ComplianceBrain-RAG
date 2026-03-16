import numpy as np
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from tqdm import tqdm
import time
from dotenv import load_dotenv
import os

load_dotenv()

COLLECTION_NAME = "regulatory_rag"

print("🔵 Loading embedding model...")
model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
    api_key= os.getenv("NVIDIA_API_KEY"),
    truncate="NONE"
)

print("🔵 Connecting Qdrant...")
client = QdrantClient(host="localhost", port=6333)

# -------- LOAD FULL CORPUS --------

print("🔵 Loading corpus from Qdrant (this may take time)...")

corpus = []
id_to_payload = {}
id_list = []

scroll_offset = None
total = 0

while True:

    points, scroll_offset = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=500,
        offset=scroll_offset
    )

    for p in tqdm(points, desc="Loading batch"):
        corpus.append(p.payload["text"].split())
        id_to_payload[p.id] = p.payload
        id_list.append(p.id)

    total += len(points)
    print("Loaded:", total)

    if scroll_offset is None:
        break

print("Final corpus size:", total)

print("🔵 Building BM25 index...")
bm25 = BM25Okapi(corpus)
print("✅ BM25 ready")


def hybrid_search(query, top_k=30):

    print("\n🔎 Embedding query...")
    start_time = time.time()

    query_vector = model.embed_query(query)

    print("🔎 Vector searching...")
    vector_hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=50
    ).points

    vector_scores = {hit.id: hit.score for hit in vector_hits}

    print("🔎 Running BM25 scoring...")
    tokenized_query = query.split()

    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_top_idx = np.argsort(bm25_scores)[::-1][:50]

    bm25_scores_dict = {
        id_list[i]: bm25_scores[i] for i in bm25_top_idx
    }

    max_bm = max(bm25_scores_dict.values()) if bm25_scores_dict else 1

    bm25_scores_dict = {
        k: v / max_bm for k, v in bm25_scores_dict.items()
    }

    print("🔎 Fusing scores...")

    candidate_ids = set(vector_scores.keys()) | set(bm25_scores_dict.keys())

    hybrid_scores = {}

    for cid in candidate_ids:
        vec = vector_scores.get(cid, 0)
        bm = bm25_scores_dict.get(cid, 0)
        hybrid_scores[cid] = 0.7 * vec + 0.3 * bm

    ranked = sorted(
        hybrid_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    end_time = time.time()
    print(f"⚡ Retrieval completed in {end_time - start_time:.2f} sec")

    results = []

    for rank, (pid, score) in enumerate(ranked):

        payload = id_to_payload[pid]

        print("\n----------------------")
        print(f"Rank: {rank+1}")
        print(f"Hybrid Score: {score:.4f}")
        print(f"Regulation: {payload.get('regulation')}")
        print(f"Clause: {payload.get('clause_number')}")
        print(f"Topic: {payload.get('topic')}")
        print("\nText Preview:")
        print(payload.get("text")[:400])

        # ⭐ BUILD RESULT OBJECT (VERY IMPORTANT)
        results.append({
            "id": pid,
            "score": score,
            "text": payload.get("text"),
            "regulation": payload.get("regulation"),
            "clause": payload.get("clause_number"),
            "topic": payload.get("topic"),
            "page": payload.get("page")
        })

    # ⭐⭐⭐ MOST IMPORTANT LINE ⭐⭐⭐
    return results

if __name__ == "__main__":
    while True:
        q = input("\nAsk Compliance Question: ")
        hybrid_search(q)