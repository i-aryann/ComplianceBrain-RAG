from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

client = ChatGroq(
    model="openai/gpt-oss-120b",
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
        return "LLM generation failed."


def stream_answer(prompt):
    """
    Generator — yields text chunks as the LLM produces them.
    Uses LangChain's .stream() which calls the provider's streaming API,
    so tokens arrive at the client in real-time, not after full completion.
    """
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user",   "content": prompt}
    ]
    try:
        for chunk in client.stream(messages):
            # LangChain AIMessageChunk has a .content attribute
            token = chunk.content
            if token:
                yield token
    except Exception as e:
        print("❌ LLM STREAM ERROR:", str(e))
        yield "LLM generation failed."