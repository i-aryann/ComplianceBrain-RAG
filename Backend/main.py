from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from D_rag_pipeline.d_pipeline import RAGPipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create pipeline once at startup (loads embedding model + BM25 index)
rag = RAGPipeline()


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask-stream")
def ask_stream(q: Query):
    """
    True streaming endpoint.

    Tokens arrive at the client the moment the LLM produces them —
    no buffering, no fake time.sleep delay.

    Protocol:
      • Regular chunks : plain text (LLM tokens, may be multi-char)
      • Final line     : "\\n__SOURCES__:<json-array>"
    """
    return StreamingResponse(
        rag.run_stream(q.question),
        media_type="text/plain",
        headers={
            # Disable any proxy/nginx buffering so chunks reach browser immediately
            "X-Accel-Buffering": "no",
            "Cache-Control":     "no-cache",
        }
    )