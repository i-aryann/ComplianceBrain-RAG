def build_context(chunks):
    """
    Build a formatted context string from retrieved chunks.

    Each chunk dict can come from two places:
      - hybrid_search  → keys: text, regulation, clause, page, doc_id
      - reranker       → returns original Qdrant payload dicts
                          keys: text, regulation, clause_number, page, doc_id

    We handle both key names gracefully so context is never empty.
    """
    context = ""

    for i, ch in enumerate(chunks):
        # Support both 'clause' (hybrid_search output) and 'clause_number' (raw payload)
        clause = ch.get("clause") or ch.get("clause_number") or "N/A"
        page   = ch.get("page") or "N/A"
        regulation = ch.get("regulation") or "N/A"
        source = ch.get("source_file") or ch.get("doc_id") or "N/A"
        topic  = ch.get("topic") or "N/A"
        text   = ch.get("text", "")

        context += f"""
[Document {i+1}]
Regulation : {regulation}
Document   : {source}
Topic      : {topic}
Clause     : {clause}
Page       : {page}
Text:
{text}
"""
    return context