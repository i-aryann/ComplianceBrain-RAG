from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from qdrant_client import QdrantClient

load_dotenv()

COLLECTION_NAME = "regulatory_rag"

model = NVIDIAEmbeddings(
    model="nvidia/nv-embed-v1",
    truncate="NONE"
)

client = QdrantClient(host="localhost", port=6333)


def search(query):

    query_vector = model.embed_query(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=5
    )

    for r in results.points:
        print("\nScore:", r.score)
        print("Topic:", r.payload["topic"])
        print("Text:", r.payload["text"][:200])


q = input("Ask your query:")
search(q)