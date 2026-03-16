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
        sources = [
            c.get("doc_id", "unknown")
            for c in context_chunks
        ]

        return {
            "answer": answer,
            "sources": sources
        }