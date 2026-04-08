from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
from D_rag_pipeline.d_pipeline import RAGPipeline
import json
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
    """
    Streams the answer word-by-word (SSE-style plain text), then
    finalises with a JSON line carrying structured source citations.
    
    Protocol:
      • Every token line:  plain text word(s) followed by a space
      • Final line:        "__SOURCES__:<json-array>"
    """

    def generate():

        print("\n🔥 STREAM QUERY:", q.question)

        result = rag.run(q.question)

        answer  = result.get("answer", "")
        sources = result.get("sources", [])

        # Stream answer token by token
        words = answer.split(" ")
        for w in words:
            if w:
                yield w + " "
                time.sleep(0.03)

        # After answer is done, emit structured sources on a sentinel line
        sources_json = json.dumps(sources, ensure_ascii=False)
        yield f"\n__SOURCES__:{sources_json}"

        print("✅ STREAM COMPLETE\n")

    return StreamingResponse(generate(), media_type="text/plain")