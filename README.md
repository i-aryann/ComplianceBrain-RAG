ComplianceBrain-RAG 🧠📚

AI-Powered Regulatory Compliance Assistant using Retrieval Augmented Generation (RAG).

ComplianceBrain-RAG is an intelligent system designed to help users understand and query complex financial and regulatory guidelines such as RBI circulars, Basel norms, and audit requirements.
It uses modern LLM + Vector Database architecture to provide accurate, contextual, and source-grounded answers.

🚀 Features

🔎 Ask natural language questions about regulations

📄 Retrieves relevant regulatory documents

🤖 Generates context-aware answers using LLM

📚 Source-based responses (reduces hallucination)

⚡ Fast semantic search with vector embeddings

🧩 Modular and production-ready architecture

🏗️ Tech Stack

Python

LangChain / LangGraph

Qdrant (Vector Database)

Embedding Models (OpenAI / HuggingFace)

LLM (OpenAI / Local Model)

Docker

FastAPI / Streamlit (for UI – optional)

📂 Project Structure
ComplianceBrain-RAG/
│
├── data/                 # Regulatory PDFs / circulars
├── ingestion/            # Data loading & chunking scripts
├── embeddings/           # Embedding generation
├── vectorstore/          # Qdrant setup & configs
├── rag_pipeline/         # Retrieval + generation logic
├── app/                  # API or UI application
├── requirements.txt
└── README.md