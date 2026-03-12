from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

COLLECTION_NAME = "regulatory_rag"

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

client = QdrantClient(host="localhost", port=6333)


def search(query, top_k=5):

    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    for i, r in enumerate(results.points):

        payload = r.payload

        print("\n----------------------")
        print(f"Rank: {i+1}")
        print(f"Score: {r.score:.4f}")
        print(f"Regulation: {payload['regulation']}")
        print(f"Clause: {payload['clause_number']}")
        print(f"Topic: {payload['topic']}")
        print(f"Source: {payload['source_file']} | Page {payload['page']}")
        print("\nText Preview:")
        print(payload["text"][:500])


if __name__ == "__main__":

    while True:
        q = input("\nAsk Compliance Question: ")
        search(q)