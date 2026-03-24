# Regulatory Compliance Assistant (Hybrid RAG System)

An end-to-end Retrieval-Augmented Generation (RAG) system designed to assist with integit commitrpretation and analysis of financial regulatory documents such as RBI Master Directions, Basel guidelines, and SEBI regulations.

This project focuses on building a production-thinking AI system that can retrieve, interpret, and reason over compliance obligations using modern retrieval engineering techniques

---

## Overview

Financial institutions and consulting firms deal with large volumes of regulatory documentation. Manually locating relevant clauses and interpreting obligations is time-consuming and error-prone.

This system demonstrates how hybrid retrieval and LLM-driven reasoning can be combined to enable:

* Clause-level semantic search across regulatory documents
* Context-grounded compliance answers
* Regulation comparison workflows
* Automated compliance checklist generation

The goal of the project is to simulate real enterprise document intelligence use-cases.

---

## Key Features

* Hybrid Retrieval (Vector + BM25) for high-precision clause discovery
* Cross-Encoder Reranking to improve relevance of top results
* Metadata-aware search (filter by regulation, topic, clause number)
* Legal-aware document chunking and preprocessing pipeline
* Compliance risk reasoning workflows
* Interactive Streamlit interface for natural language querying
* Containerized deployment setup

---

## System Architecture

The pipeline consists of the following stages:

1. Regulatory document ingestion and parsing
2. Clause-aware segmentation and metadata enrichment
3. Embedding generation and vector indexing in Qdrant
4. Hybrid retrieval and reranking
5. LLM-based grounded answer generation
6. UI layer for user interaction

This design reflects practical considerations around retrieval accuracy, latency, and explainability.

---

## Dataset

The corpus includes publicly available regulatory documents such as:

* RBI Master Directions (KYC, NBFC regulation, digital lending)
* Basel Committee banking supervision frameworks
* SEBI regulatory guidelines
* Selected corporate governance and compliance circulars

All documents are processed into structured clause-level chunks for retrieval.

---

## Tech Stack

* Python
* Qdrant Vector Database
* Sentence Transformers (BGE Embeddings)
* Rank-BM25
* Streamlit
* Docker

---

## Evaluation Approach

Retrieval quality was evaluated using curated compliance queries measuring:

* Top-k retrieval relevance
* Citation grounding
* Latency performance
* Impact of hybrid retrieval vs pure vector search

These experiments helped tune chunking strategy, embedding selection, and score fusion.

---

## Running the Project

### 1. Start Vector Database

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```

---

## Future Improvements

* Multi-modal document understanding (tables / scanned PDFs)
* Real-time regulatory update ingestion
* Advanced agentic workflows for compliance audits
* Cloud deployment with scalable vector indexing

---

## Motivation

This project was built to explore how retrieval-focused AI systems can support regulatory interpretation workflows in banking, consulting, and fintech environments.

It emphasizes engineering trade-offs such as retrieval accuracy vs latency, open-source vs API-based models, and explainability in high-stakes document intelligence systems.

---

## Author

Aryan Gupta
Data & AI Enthusiast focused on Retrieval Engineering, NLP Systems and Applied Analytics.
