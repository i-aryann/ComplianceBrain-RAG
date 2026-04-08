from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Groq client ──────────────────────────────────────────────────────────────
# Valid Groq models: llama-3.3-70b-versatile, llama3-70b-8192, mixtral-8x7b-32768
client = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

_SYSTEM = "You are a regulatory compliance expert."


def generate_answer(prompt):
    """Blocking call — returns the full answer as a string."""
    try:
        messages = [
            {"role": "system", "content": _SYSTEM},
            {"role": "user",   "content": prompt}
        ]
        response = client.invoke(messages)
        return response.content
    except Exception as e:
        print("❌ LLM ERROR:", str(e))
        return f"LLM generation failed: {str(e)}"


def stream_answer(prompt):
    """
    Generator — yields text chunks as the LLM produces them.
    Uses LangChain .stream() for real token-by-token streaming.
    """
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user",   "content": prompt}
    ]
    try:
        for chunk in client.stream(messages):
            token = chunk.content
            if token:
                yield token
    except Exception as e:
        print("❌ LLM STREAM ERROR:", str(e))
        yield f"LLM generation failed: {str(e)}"