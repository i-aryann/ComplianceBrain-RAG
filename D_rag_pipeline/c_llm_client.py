from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

client = ChatGroq(
  model="openai/gpt-oss-120b",
  api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(prompt):

    try:

        messages = [
            {"role": "system", "content": "You are a regulatory compliance expert."},
            {"role": "user", "content": prompt}
        ]

        response = client.invoke(messages)

        return response.content

    except Exception as e:

        print("❌ LLM ERROR:", str(e))
        return "LLM generation failed."

    return response.choices[0].message.content