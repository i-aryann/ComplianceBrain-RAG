import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from B_query_retrieval.b_hybrid_search import hybrid_search
from C_query_reranking.a_cross_encoding import rerank
from D_rag_pipeline.a_context_builder import build_context
from D_rag_pipeline.b_prompt_template import build_prompt
from D_rag_pipeline.c_llm_client import generate_answer, stream_answer


def _build_sources(context_chunks):
    """Extract structured citation objects from retrieved chunks."""
    sources = []
    seen = set()

    for c in context_chunks:
        clause      = c.get("clause") or c.get("clause_number") or "N/A"
        page        = c.get("page") or "N/A"
        regulation  = c.get("regulation") or "N/A"
        source_file = c.get("source_file") or "N/A"
        topic       = c.get("topic") or "N/A"
        doc_id      = c.get("doc_id") or f"{regulation} | {source_file} | Clause {clause}"

        if doc_id in seen:
            continue
        seen.add(doc_id)

        sources.append({
            "doc_id":      doc_id,
            "regulation":  regulation,
            "source_file": source_file,
            "clause":      clause,
            "page":        page,
            "topic":       topic,
        })

    return sources


class RAGPipeline:

    # ──────────────────────────────────────────────
    # Blocking path (kept for CLI testing)
    # ──────────────────────────────────────────────
    def run(self, query):

        results = hybrid_search(query, top_k=30) or []
        if not results:
            return {"answer": "No regulatory chunks retrieved.", "sources": []}

        top_chunks = rerank(query, results) or results
        context_chunks = top_chunks[:5]

        context = build_context(context_chunks)
        prompt  = build_prompt(query, context)
        answer  = generate_answer(prompt)
        sources = _build_sources(context_chunks)

        return {"answer": answer, "sources": sources}

    # ──────────────────────────────────────────────
    # True streaming path  ← used by /ask-stream
    # ──────────────────────────────────────────────
    def run_stream(self, query):
        """
        Generator that:
          1. Runs retrieval + reranking synchronously (fast, ~1-2 s)
          2. Immediately starts yielding LLM tokens as they arrive
          3. Finishes with a sentinel line carrying structured citations

        Protocol consumed by the frontend:
          • Regular tokens  → plain text chunks
          • Final sentinel  → "\\n__SOURCES__:<json-array>"
        """

        # ── Step 1: Retrieval (blocks until done, but this is fast) ──
        print("\n🔥 STREAM QUERY:", query)
        results = hybrid_search(query, top_k=30) or []

        if not results:
            yield "No regulatory chunks retrieved."
            yield "\n__SOURCES__:[]"
            return

        # ── Step 2: Rerank ──
        top_chunks = rerank(query, results) or results
        context_chunks = top_chunks[:5]

        # ── Step 3: Build context + prompt ──
        context = build_context(context_chunks)
        prompt  = build_prompt(query, context)

        # ── Step 4: Stream LLM tokens as they arrive ──
        print("🚀 Streaming LLM response...")
        for token in stream_answer(prompt):
            yield token

        # ── Step 5: Append sources sentinel ──
        sources = _build_sources(context_chunks)
        sources_json = json.dumps(sources, ensure_ascii=False)
        yield f"\n__SOURCES__:{sources_json}"

        print("✅ STREAM COMPLETE\n")