from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from D_rag_pipeline.d_pipeline import RAGPipeline
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create pipeline once at startup
rag = RAGPipeline()


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask-stream")
def ask_stream(q: Query):
    """
    True streaming endpoint — LLM tokens reach the frontend as they are generated.

    Protocol:
      • Regular chunks : plain LLM text (streamed token by token)
      • Final sentinel : "\\n__SOURCES__:<json-array>"
    """
    return StreamingResponse(
        rag.run_stream(q.question),
        media_type="text/plain",
        headers={
            "X-Accel-Buffering": "no",   # disable nginx buffering
            "Cache-Control":     "no-cache",
        }
    )