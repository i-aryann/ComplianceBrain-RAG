import sys
import os
import time
import streamlit as st

# ---------- FIX PROJECT ROOT IMPORT ----------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from D_rag_pipeline.d_pipeline import RAGPipeline


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Regulatory AI Assistant",
    page_icon="📊",
    layout="centered"
)

# ---------- DARK THEME CSS ----------
st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.big-title {
    font-size: 42px;
    font-weight: 700;
    color: #4da3ff;
}

.answer-card {
    background-color: #1c1f26;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #2c313c;
    margin-top: 12px;
    line-height: 1.8;
    font-size: 16px;
    color: #e6edf3;
}

.source-chip {
    background-color: #232733;
    padding: 10px 14px;
    border-radius: 10px;
    margin-top: 8px;
    color: #9fb3c8;
    border: 1px solid #2c313c;
}

.latency {
    color: #8b949e;
    font-size: 12px;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)


# ---------- ANSWER FORMATTER ----------
def format_answer(text):
    text = text.replace("1.", "\n\n• ")
    text = text.replace("2.", "\n\n• ")
    text = text.replace("3.", "\n\n• ")
    text = text.replace("4.", "\n\n• ")
    text = text.replace("5.", "\n\n• ")
    return text


# ---------- LOAD PIPELINE ----------
@st.cache_resource
def load_pipeline():
    return RAGPipeline()

pipeline = load_pipeline()


# ---------- SIDEBAR ----------
with st.sidebar:

    st.title("⚙️ Control Panel")

    if st.button("🧹 Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("### 🧠 System Status")
    st.success("RAG Pipeline Ready")

    st.markdown("### 🔎 Retrieval Stack")
    st.write("• Hybrid Search")
    st.write("• Cross Encoder Reranker")
    st.write("• Context Optimization")
    st.write("• Grounded LLM Answer")

    st.markdown("---")
    st.caption("Regulatory Intelligence System")


# ---------- TITLE ----------
st.markdown(
    '<div class="big-title">📊 Regulatory Compliance AI</div>',
    unsafe_allow_html=True
)

st.caption("Ask RBI / SEBI / NBFC regulatory questions")


# ---------- CHAT STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- SHOW CHAT ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)


# ---------- INPUT ----------
query = st.chat_input("Ask a compliance question...")

if query:

    # USER
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )

    with st.chat_message("user"):
        st.markdown(query)

    # ASSISTANT
    with st.chat_message("assistant"):

        placeholder = st.empty()

        start = time.time()

        try:
            result = pipeline.run(query)

            latency = round(time.time() - start, 2)

            answer = format_answer(result["answer"])
            sources = result["sources"]

            # STREAM EFFECT
            streamed = ""
            for word in answer.split():
                streamed += word + " "
                placeholder.markdown(
                    f'<div class="answer-card">{streamed}▌</div>',
                    unsafe_allow_html=True
                )
                time.sleep(0.008)

            placeholder.markdown(
                f'<div class="answer-card">{streamed}</div>',
                unsafe_allow_html=True
            )

            # SOURCES
            st.markdown("### 📚 Sources")
            for s in sources:
                st.markdown(
                    f'<div class="source-chip">📄 {s}</div>',
                    unsafe_allow_html=True
                )

            # LATENCY
            st.markdown(
                f'<div class="latency">⏱ Response Time: {latency} sec</div>',
                unsafe_allow_html=True
            )

            st.session_state.messages.append(
                {"role": "assistant", "content": streamed}
            )

        except Exception as e:
            st.error("Pipeline Error")
            st.exception(e)