import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from B_query_retrieval.b_hybrid_search import hybrid_search
from C_query_reranking.a_cross_encoding import rerank
from D_rag_pipeline.a_context_builder import build_context
from D_rag_pipeline.b_prompt_template import build_prompt
from D_rag_pipeline.c_llm_client import generate_answer


class RAGPipeline:

    def run(self, query):

        # ---------- RETRIEVAL ----------
        results = hybrid_search(query, top_k=30) or []

        if len(results) == 0:
            return {
                "answer": "No regulatory chunks retrieved.",
                "sources": []
            }

        # ---------- RERANK ----------
        top_chunks = rerank(query, results) or []

        if len(top_chunks) == 0:
            top_chunks = results

        # ---------- CONTEXT ----------
        context_chunks = top_chunks[:5]

        context = build_context(context_chunks)

        # ---------- PROMPT ----------
        prompt = build_prompt(query, context)

        # ---------- LLM ----------
        answer = generate_answer(prompt)

        # ---------- SOURCES ----------
        # Build structured source objects for the frontend
        sources = []
        seen = set()

        for c in context_chunks:
            # Handle both key styles (hybrid_search vs raw Qdrant payload)
            clause = c.get("clause") or c.get("clause_number") or "N/A"
            page   = c.get("page") or "N/A"
            regulation = c.get("regulation") or "N/A"
            source_file = c.get("source_file") or "N/A"
            topic  = c.get("topic") or "N/A"
            doc_id = c.get("doc_id") or f"{regulation} | {source_file} | Clause {clause}"

            # Deduplicate by doc_id
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

        return {
            "answer":  answer,
            "sources": sources
        }