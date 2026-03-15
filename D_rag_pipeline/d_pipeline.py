import sys
import os

# IMPORTANT → allow running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from B_query_retrieval.b_hybrid_search import hybrid_search
from C_query_reranking.a_cross_encoding import rerank
from D_rag_pipeline.a_context_builder import build_context
from D_rag_pipeline.b_prompt_template import build_prompt
from D_rag_pipeline.c_llm_client import generate_answer


def rag_answer(query):

    print("\n🔎 Running Hybrid Retrieval...\n")

    # ---------- RETRIEVAL ----------
    results = hybrid_search(query, top_k=30)

    if results is None:
        results = []

    print("✅ Results count:", len(results))

    if len(results) == 0:
        return "No regulatory chunks retrieved."

    # ---------- RERANK ----------
    print("\n🔎 Running Reranker...\n")

    top_chunks = rerank(query, results)

    if top_chunks is None:
        top_chunks = []

    print("✅ Reranked count:", len(top_chunks))

    # DEBUG SAMPLE
    if len(top_chunks) > 0:
        print("\n⭐ Sample Reranked Chunk:\n")
        print(top_chunks[0])

    # ---------- FALLBACK SAFETY ----------
    if len(top_chunks) == 0:
        print("\n⚠ Reranker returned empty → Using Hybrid Results\n")
        top_chunks = results

    # ---------- CONTEXT ----------
    context_chunks = top_chunks[:5]

    print("\n📦 Building Context with chunks:", len(context_chunks))

    context = build_context(context_chunks)

    # ---------- PROMPT ----------
    prompt = build_prompt(query, context)

    # ---------- LLM ----------
    print("\n🤖 Generating Answer...\n")

    answer = generate_answer(prompt)

    return answer


# ---------- CLI RUN ----------
if __name__ == "__main__":

    while True:

        query = input("\nEnter compliance question (or type exit): ")

        if query.lower() == "exit":
            break

        try:
            ans = rag_answer(query)

            print("\n✅ FINAL ANSWER:\n")
            print(ans)

        except Exception as e:
            print("\n❌ PIPELINE ERROR:")
            print(str(e))