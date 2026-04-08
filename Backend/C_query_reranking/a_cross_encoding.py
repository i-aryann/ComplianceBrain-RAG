"""
a_cross_encoding.py — NVIDIA Reranker only.

Retrieval (dense + sparse + RRF fusion) is handled entirely by
B_query_retrieval/b_hybrid_search.py.  This module's only job is
to rerank the already-retrieved docs using the NVIDIA cross-encoder.
"""

from functools import lru_cache
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import NVIDIARerank
from langchain_core.documents import Document
import os

load_dotenv()

NVIDIA_REASONING = os.getenv("NVIDIA_REASONING", "").strip()

# ── Reranker — loaded eagerly but with a graceful fallback ────────────────────
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
        print(f"⚠️  Reranker failed to load: {e} — will fall back to score order")
else:
    print("⚠️  NVIDIA_REASONING key not set — reranking disabled")


# ── rerank() ──────────────────────────────────────────────────────────────────
def rerank(query, docs, top_k=5):
    """
    Rerank docs using the NVIDIA cross-encoder.
    Falls back to top-k by retrieval score if reranker is unavailable.

    Accepts doc dicts that include all citation fields from hybrid_search:
    text, regulation, source_file, clause, clause_number, topic, page, doc_id.
    """
    if not docs:
        return []

    # Strip docs with null text (defensive)
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
            idx   = rank_doc.metadata["orig_index"]
            score = getattr(rank_doc, "score", None)
            doc   = docs[idx]
            doc["rerank_score"] = score if score is not None else 1.0
            reranked_docs.append(doc)

        return reranked_docs

    except Exception as e:
        print("❌ Reranker error:", str(e))
        return docs[:top_k]