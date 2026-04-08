import numpy as np
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from functools import lru_cache
from tqdm import tqdm
import time
from dotenv import load_dotenv
import os

load_dotenv()

COLLECTION_NAME = "regulatory_rag"
NVIDIA_API_KEY  = os.getenv("NVIDIA_API_KEY", "").strip()

# ── Qdrant client (lightweight — no network call on init) ────────────────────
print("🔵 Connecting Qdrant...")
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# ── Load BM25 corpus at startup (fast — just Qdrant scroll, no ML model) ────
print("🔵 Loading corpus from Qdrant...")

corpus       = []
id_to_payload = {}
id_list      = []

scroll_offset = None
total = 0

while True:
    points, scroll_offset = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=500,
        offset=scroll_offset
    )

    for p in tqdm(points, desc="Loading batch"):
        text = p.payload.get("text")
        if not text:
            continue
        corpus.append(text.split())
        id_to_payload[p.id] = p.payload
        id_list.append(p.id)

    total += len(points)
    if scroll_offset is None:
        break

print(f"✅ Loaded {total} chunks")

print("🔵 Building BM25 index...")
bm25 = BM25Okapi(corpus) if corpus else BM25Okapi([["placeholder"]])
print("✅ BM25 ready")

# ── Embedding model — initialised LAZILY on first query ──────────────────────
# NVIDIAEmbeddings makes a network validation call on __init__, which can take
# 30-60s. Deferring it avoids blocking the entire server startup.
_embed_model = None

def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("🔵 Loading NVIDIA embedding model (first query)...")
        _embed_model = NVIDIAEmbeddings(
            model="nvidia/nv-embed-v1",
            api_key=NVIDIA_API_KEY,
            truncate="NONE"
        )
        print("✅ Embedding model ready")
    return _embed_model


@lru_cache(maxsize=256)
def _embed_cached(query: str):
    return tuple(_get_embed_model().embed_query(query))


def hybrid_search(query, top_k=30):

    print("\n🔎 Embedding query...")
    start_time = time.time()

    # ── Dense (vector) search ──────────────────────────────────────────────
    vec = list(_embed_cached(query))

    dense_results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vec,
        limit=top_k
    )
    dense_hits = [r.payload for r in dense_results.points]

    # ── Sparse (BM25) search ───────────────────────────────────────────────
    scores   = bm25.get_scores(query.lower().split())
    top_idx  = np.argsort(scores)[::-1][:top_k]
    bm25_hits = [id_to_payload[id_list[i]] for i in top_idx if i < len(id_list)]

    # ── RRF fusion ─────────────────────────────────────────────────────────
    score_map = {}
    for r, d in enumerate(dense_hits):
        t = d.get("text") or ""
        score_map[t] = score_map.get(t, 0) + 1 / (60 + r)
    for r, d in enumerate(bm25_hits):
        t = d.get("text") or ""
        score_map[t] = score_map.get(t, 0) + 1 / (60 + r)

    fused = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    text_to_payload = {d.get("text", ""): d for d in dense_hits + bm25_hits}

    ranked = [(t, s) for t, s in fused if t in text_to_payload][:top_k]

    end_time = time.time()
    print(f"⚡ Retrieval completed in {end_time - start_time:.2f} sec")

    results = []
    for rank, (text, score) in enumerate(ranked):
        payload = text_to_payload[text]

        # Debug print
        print(f"\n--- Rank {rank+1} | Score {score:.4f}")
        print(f"Regulation : {payload.get('regulation')}")
        print(f"Source     : {payload.get('source_file')}")
        print(f"Clause     : {payload.get('clause_number')}")
        print(f"Page       : {payload.get('page')}")

        results.append({
            "id":              payload.get("doc_id", rank),
            "score":           score,
            "text":            payload.get("text"),
            "regulation":      payload.get("regulation"),
            "source_file":     payload.get("source_file"),
            "clause":          payload.get("clause_number"),
            "clause_number":   payload.get("clause_number"),
            "topic":           payload.get("topic"),
            "page":            payload.get("page"),
            "regulation_type": payload.get("regulation_type"),
            "doc_id":          payload.get("doc_id") or f"{payload.get('regulation','?')} | {payload.get('source_file','?')} | Clause {payload.get('clause_number','?')}",
        })

    return results