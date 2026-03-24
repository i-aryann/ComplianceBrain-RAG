from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from D_rag_pipeline.d_pipeline import RAGPipeline
from fastapi.responses import StreamingResponse
import time

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⭐ create pipeline object ONCE (important for performance)
rag = RAGPipeline()


class Query(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask-stream")
def ask_stream(q: Query):

    def generate():

        print("\n🔥 STREAM QUERY:", q.question)

        result = rag.run(q.question)

        answer = result["answer"]

        # simulate token streaming
        words = answer.split()

        for w in words:
            yield w + " "
            time.sleep(0.03)   # control speed

        print("✅ STREAM COMPLETE\n")

    return StreamingResponse(generate(), media_type="text/plain")