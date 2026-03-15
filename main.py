import time
import sys

# import RAG pipeline
from D_rag_pipeline.d_pipeline import rag_answer


def run_cli():

    print("\n==============================")
    print("📘 Regulatory Compliance RAG")
    print("==============================\n")

    while True:

        query = input("Enter compliance question (or type exit): ")

        if query.lower() == "exit":
            print("Exiting system.")
            sys.exit()

        try:
            start = time.time()

            answer = rag_answer(query)

            end = time.time()

            print("\n✅ ANSWER:\n")
            print(answer)

            print(f"\n⏱ Response Time: {round(end - start, 2)} sec\n")

        except Exception as e:
            print("\n❌ ERROR OCCURRED:")
            print(str(e))
            print("\nCheck retrieval / reranker / LLM connection.\n")


if __name__ == "__main__":
    run_cli()