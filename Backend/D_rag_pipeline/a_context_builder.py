def build_context(chunks):
    context = ""

    for i, ch in enumerate(chunks):
        context += f"""
[Document {i+1}]
Regulation: {ch['regulation']}
Clause: {ch['clause']}
Page: {ch['page']}
Text:
{ch['text']}
"""
    return context