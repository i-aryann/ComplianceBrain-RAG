import time
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

# ==============================
# CONFIG
# ==============================

COLLECTION_NAME = "regulatory_rag"
TOP_K_VECTOR = 40
TOP_K_BM25 = 40
RERANK_TOP_K = 20
FINAL_TOP_K = 5

# ==============================
# BULLETPROOF JSONL LOADER
# ==============================

def load_jsonl_chunks(file_path, min_len=20):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    docs = []
    skipped = 0

    with open(file_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()

            if not line:
                skipped += 1
                continue

            try:
                row = json.loads(line)
                text = row.get("text", "").strip()

                if len(text) >= min_len:
                    docs.append({"text": text})
                else:
                    skipped += 1

            except Exception:
                skipped += 1

    # remove duplicates
    unique = {}
    for d in docs:
        unique[d["text"]] = d

    docs = list(unique.values())

    print(f"✅ Loaded chunks: {len(docs)}")
    print(f"⚠️ Skipped rows: {skipped}")

    return docs

# ==============================
# LOAD MODELS
# ==============================

print("Loading embedding model...")
embed_model = SentenceTransformer("BAAI/bge-base-en")

print("Loading reranker...")
reranker = CrossEncoder("BAAI/bge-reranker-base")

# ==============================
# CONNECT QDRANT
# ==============================

client = QdrantClient("localhost", port=6333)

# ==============================
# LOAD CHUNKS FOR BM25
# ==============================

DATA_PATH = r"E:\Projects\RegulatoryRAG\chunks.jsonl"

docs = load_jsonl_chunks(DATA_PATH)

corpus = [d["text"] for d in docs]
tokenized_corpus = [doc.split() for doc in corpus]

bm25 = BM25Okapi(tokenized_corpus)

# ==============================
# DENSE SEARCH
# ==============================

def dense_search(query):

    q_vec = embed_model.encode(query).tolist()

    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=q_vec,
        limit=TOP_K_VECTOR,
        with_payload=True
    )

    results = []

    for rank, point in enumerate(hits.points):
        text = point.payload.get("text", "").strip()

        if text:
            results.append({
                "text": text,
                "dense_rank": rank + 1
            })

    return results

# ==============================
# BM25 SEARCH
# ==============================

def bm25_search(query):

    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    top_idx = np.argsort(scores)[::-1][:TOP_K_BM25]

    results = []

    for rank, idx in enumerate(top_idx):
        results.append({
            "text": corpus[idx],
            "bm25_rank": rank + 1
        })

    return results

# ==============================
# RECIPROCAL RANK FUSION
# ==============================

def reciprocal_rank_fusion(dense, sparse, k=60):

    fused = {}

    for item in dense:
        fused.setdefault(item["text"], 0)
        fused[item["text"]] += 1 / (k + item["dense_rank"])

    for item in sparse:
        fused.setdefault(item["text"], 0)
        fused[item["text"]] += 1 / (k + item["bm25_rank"])

    ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)

    return [r[0] for r in ranked[:RERANK_TOP_K]]

# ==============================
# RERANKER
# ==============================

def rerank(query, chunks):

    if not chunks:
        return []

    pairs = [[query, c] for c in chunks]

    scores = reranker.predict(pairs, batch_size=8)

    ranked = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [r[0] for r in ranked[:FINAL_TOP_K]]

# ==============================
# CONTEXT BUILDER
# ==============================

def build_context(top_chunks):

    return "\n\n".join(top_chunks)

# ==============================
# FULL PIPELINE
# ==============================

def hybrid_rag_pipeline(query):

    start = time.time()

    print("\n🔎 Dense searching...")
    dense = dense_search(query)

    print("🔎 BM25 searching...")
    sparse = bm25_search(query)

    print("⚡ Rank fusion...")
    fused_chunks = reciprocal_rank_fusion(dense, sparse)

    print("🧠 Reranking...")
    best_chunks = rerank(query, fused_chunks)

    context = build_context(best_chunks)

    end = time.time()

    print(f"\n✅ Retrieval completed in {round(end-start,2)} sec")

    return context, best_chunks

# ==============================
# TEST
# ==============================

if __name__ == "__main__":

    query = "What are NBFC KYC periodic update rules?"

    context, chunks = hybrid_rag_pipeline(query)

    print("\n====== FINAL CONTEXT ======")
    print(context)

    print("\n====== TOP CHUNKS ======")
    for c in chunks:
        print("-", c[:150])