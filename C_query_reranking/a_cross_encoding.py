import numpy as np
from functools import lru_cache
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings, NVIDIARerank
from langchain_core.documents import Document
import os

load_dotenv()

COLLECTION = "regulatory_rag"

# ================= MODELS =================
embed_model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
    truncate="NONE"
)

reranker = NVIDIARerank(
    model="nv-rerank-qa-mistral-4b:1",
    top_n=5
)

# ================= QDRANT =================
client = QdrantClient(host="localhost", port=6333)

print("Loading chunks for BM25...")

scroll = client.scroll(
    collection_name=COLLECTION,
    limit=10000,
    with_payload=True,
    with_vectors=False
)

ALL_CHUNKS = [p.payload for p in scroll[0]]
TOKENIZED = [c["text"].lower().split() for c in ALL_CHUNKS]
bm25 = BM25Okapi(TOKENIZED)

print("Loaded:", len(ALL_CHUNKS))


# ================= EMBEDDING CACHE =================
@lru_cache(maxsize=128)
def embed_cached(query):
    return tuple(embed_model.embed_query(query))


# ================= DENSE =================
def dense_search(query, k=40):

    vec = list(embed_cached(query))

    res = client.query_points(
        collection_name=COLLECTION,
        query=vec,
        limit=k
    )

    return [r.payload for r in res.points]


# ================= SPARSE =================
def sparse_search(query, k=40):

    scores = bm25.get_scores(query.lower().split())
    idx = np.argsort(scores)[::-1][:k]

    return [ALL_CHUNKS[i] for i in idx]


# ================= RRF =================
def rrf_fusion(dense, sparse):

    score = {}

    for r, d in enumerate(dense):
        score[d["text"]] = score.get(d["text"], 0) + 1/(60+r)

    for r, d in enumerate(sparse):
        score[d["text"]] = score.get(d["text"], 0) + 1/(60+r)

    fused = sorted(score.items(), key=lambda x: x[1], reverse=True)

    text_map = {c["text"]: c for c in dense + sparse}

    return [text_map[t[0]] for t in fused[:12]]   # tuned


# ================= NVIDIA RERANK =================
from langchain_core.documents import Document

def rerank(query, docs, top_k=5):

    if docs is None or len(docs) == 0:
        return []

    try:

        print("🔎 Calling NVIDIA Reranker...")

        # ⭐ Convert dict docs → LangChain Documents
        lc_docs = [
            Document(page_content=d["text"], metadata={"orig_index": i})
            for i, d in enumerate(docs)
        ]

        ranked = reranker.compress_documents(
            query=query,
            documents=lc_docs
        )

        reranked_docs = []

        for rank_doc in ranked[:top_k]:

            idx = rank_doc.metadata["orig_index"]

            # NVIDIA may not return score → assign rank score
            score = getattr(rank_doc, "score", None)

            doc = docs[idx]
            doc["rerank_score"] = score if score is not None else 1.0

            reranked_docs.append(doc)

        return reranked_docs

    except Exception as e:
        print("❌ Reranker failed:", str(e))
        return []
# ================= CONTEXT =================
def build_context(chunks):

    return "\n\n".join([
        f"[Clause {c['clause_number']} | {c['topic']}]\n{c['text']}"
        for c in chunks
    ])


# ================= FULL PIPELINE =================
def hybrid_rag(query):

    print("Dense search...")
    dense = dense_search(query)

    print("Sparse search...")
    sparse = sparse_search(query)

    print("Fusion...")
    fused = rrf_fusion(dense, sparse)

    print("Reranking...")
    best = rerank(query, fused)

    context = build_context(best)

    return context


# ================= TEST =================
if __name__ == "__main__":

    q = input("Search query:")

    ctx = hybrid_rag(q)

    print("\nFINAL CONTEXT:\n")
    print(ctx[:1500])