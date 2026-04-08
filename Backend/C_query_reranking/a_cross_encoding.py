import numpy as np
from functools import lru_cache
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, NVIDIARerank
from langchain_core.documents import Document
import os

load_dotenv()

NVIDIA_API_KEY  = os.getenv("NVIDIA_API_KEY", "").strip()
NVIDIA_REASONING = os.getenv("NVIDIA_REASONING", "").strip()
COLLECTION = "regulatory_rag"

if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY not set in .env")

# ── Embedding model (used for dense search) ───────────────────────────────────
embed_model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
    api_key=NVIDIA_API_KEY,
    truncate="NONE"
)

# ── Reranker (optional — falls back gracefully if key is missing) ─────────────
reranker = None
if NVIDIA_REASONING:
    try:
        reranker = NVIDIARerank(
            model="nv-rerank-qa-mistral-4b:1",
            api_key=NVIDIA_REASONING,
            top_n=5
        )
        print("✅ NVIDIA Reranker loaded")
    except Exception as e:
        print(f"⚠️  Reranker failed to load: {e} — will skip reranking")
else:
    print("⚠️  NVIDIA_REASONING key not set — reranking disabled")

# ── Qdrant client ─────────────────────────────────────────────────────────────
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# ── Load BM25 corpus at startup ───────────────────────────────────────────────
print("Loading chunks for BM25...")

try:
    scroll = client.scroll(
        collection_name=COLLECTION,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )
    # Guard against null text fields in Qdrant payload
    ALL_CHUNKS = [p.payload for p in scroll[0] if p.payload.get("text")]
    TOKENIZED  = [c["text"].lower().split() for c in ALL_CHUNKS]
    bm25 = BM25Okapi(TOKENIZED) if TOKENIZED else BM25Okapi([["placeholder"]])
    print(f"✅ Loaded {len(ALL_CHUNKS)} chunks for BM25")
except Exception as e:
    print(f"❌ Failed to load BM25 corpus: {e}")
    ALL_CHUNKS = []
    TOKENIZED  = []
    bm25 = BM25Okapi([["placeholder"]])


# ── Embedding cache ───────────────────────────────────────────────────────────
@lru_cache(maxsize=128)
def embed_cached(query):
    return tuple(embed_model.embed_query(query))


# ── Dense search ──────────────────────────────────────────────────────────────
def dense_search(query, k=40):
    vec = list(embed_cached(query))
    res = client.query_points(
        collection_name=COLLECTION,
        query=vec,
        limit=k
    )
    return [r.payload for r in res.points]


# ── Sparse search (BM25) ──────────────────────────────────────────────────────
def sparse_search(query, k=40):
    if not ALL_CHUNKS:
        return []
    scores = bm25.get_scores(query.lower().split())
    idx = np.argsort(scores)[::-1][:k]
    return [ALL_CHUNKS[i] for i in idx]


# ── RRF fusion ────────────────────────────────────────────────────────────────
def rrf_fusion(dense, sparse):
    score = {}
    for r, d in enumerate(dense):
        t = d.get("text") or ""
        score[t] = score.get(t, 0) + 1 / (60 + r)
    for r, d in enumerate(sparse):
        t = d.get("text") or ""
        score[t] = score.get(t, 0) + 1 / (60 + r)

    fused = sorted(score.items(), key=lambda x: x[1], reverse=True)
    text_map = {c.get("text", ""): c for c in dense + sparse}
    return [text_map[t[0]] for t in fused[:12] if t[0] in text_map]


# ── NVIDIA Rerank ─────────────────────────────────────────────────────────────
def rerank(query, docs, top_k=5):
    """
    Rerank docs using NVIDIA reranker.
    Falls back to returning docs[:top_k] if reranker is unavailable.
    The docs list can contain dicts from either hybrid_search (key='clause')
    or raw Qdrant payloads (key='clause_number') — both are handled downstream.
    """
    if not docs:
        return []

    # Filter out any docs with null text
    docs = [d for d in docs if d.get("text")]

    if not docs:
        return []

    if reranker is None:
        print("⚠️  Reranker not available — returning top docs by score")
        return docs[:top_k]

    try:
        print("🔎 Calling NVIDIA Reranker...")

        lc_docs = [
            Document(page_content=d["text"], metadata={"orig_index": i})
            for i, d in enumerate(docs)
        ]

        ranked = reranker.compress_documents(query=query, documents=lc_docs)

        reranked_docs = []
        for rank_doc in ranked[:top_k]:
            idx = rank_doc.metadata["orig_index"]
            score = getattr(rank_doc, "score", None)
            doc = docs[idx]
            doc["rerank_score"] = score if score is not None else 1.0
            reranked_docs.append(doc)

        return reranked_docs

    except Exception as e:
        print("❌ Reranker failed:", str(e))
        return docs[:top_k]   # graceful fallback