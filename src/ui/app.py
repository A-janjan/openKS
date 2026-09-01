# ui/app.py
import streamlit as st
import requests
import json
import os
from time import sleep

# ---------- CONFIG ----------
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Open Knowledge Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CUSTOM CSS ----------
st.markdown(
    """
    <style>
    /* Global */
    .main {
        background: #0e1117;
        color: #f0f2f6;
    }
    .stApp {
        background: #0e1117;
    }
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
    }
    /* Search input */
    .stTextInput > div > div > input {
        background-color: #1e2230;
        color: white;
        border: 1px solid #3c3f4d;
        border-radius: 30px;
        padding: 12px 20px;
        font-size: 18px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6c63ff;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.3);
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6c63ff, #3b3b98);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 12px 28px;
        font-weight: 600;
        transition: 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.4);
    }
    /* Cards for results */
    .result-card {
        background: #1a1e2b;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        border-left: 4px solid #6c63ff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(108, 99, 255, 0.15);
    }
    .source-card {
        background: #131722;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid #2a2f3f;
    }
    .grounded-true {
        color: #4caf50;
        font-weight: 600;
        background: #1e3a1e;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    .grounded-false {
        color: #ff6b6b;
        font-weight: 600;
        background: #3e1e1e;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    .answer-text {
        font-size: 18px;
        line-height: 1.6;
        background: #1a1e2b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2a2f3f;
    }
    .footer {
        margin-top: 50px;
        text-align: center;
        color: #7a7f8a;
        font-size: 14px;
        border-top: 1px solid #2a2f3f;
        padding-top: 20px;
    }
    .footer a {
        color: #6c63ff;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    limit = st.slider("Number of chunks", min_value=3, max_value=20, value=10, step=1)
    use_rerank = st.checkbox("Use reranking", value=True)
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        "**Open Knowledge Search** combines BM25, vector search, reranking, and a knowledge graph to deliver grounded answers."
    )
    st.markdown("Built with FastAPI, PostgreSQL pgvector, Gemini, and Streamlit.")
    st.markdown("[GitHub Repository](https://github.com/your-repo)")

# ---------- MAIN UI ----------
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 48px; margin: 0;">🔍 Open Knowledge Search</h1>
        <p style="color: #9aa0b0; font-size: 18px;">Ask anything from your knowledge base</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Query input
query = st.text_input("", placeholder="e.g., How does the grift economy work?", label_visibility="collapsed")

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    search_clicked = st.button("Search", use_container_width=True)

# ---------- PROCESS QUERY ----------
if query and (search_clicked or st.session_state.get("auto_search", False)):
    st.session_state["auto_search"] = True

    with st.spinner("🔎 Searching and generating answer..."):
        try:
            payload = {"query": query, "limit": limit}
            response = requests.post(f"{API_URL}/answer", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                st.session_state["result"] = data
            else:
                st.error(f"API error: {response.status_code} – {response.text}")
                st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach API: {e}")
            st.stop()

# ---------- DISPLAY RESULTS ----------
if "result" in st.session_state:
    data = st.session_state["result"]

    # Answer section
    st.markdown("### 📝 Answer")
    col_answer, col_badge = st.columns([5, 1])
    with col_answer:
        st.markdown(f'<div class="answer-text">{data["answer"]}</div>', unsafe_allow_html=True)
    with col_badge:
        grounded = data.get("grounded", False)
        badge_class = "grounded-true" if grounded else "grounded-false"
        badge_text = "✅ Grounded" if grounded else "❌ Not grounded"
        st.markdown(f'<div class="{badge_class}">{badge_text}</div>', unsafe_allow_html=True)
        if "explanation" in data:
            with st.expander("ℹ️ Grounding explanation"):
                st.write(data["explanation"])

    # Query analysis (from /search endpoint, not in /answer response – we could call separately, but we have it from earlier)
    # We can optionally call /search to get analysis, but we skip for simplicity; we'll show the citations.

    # Citations
    citations = data.get("citations", [])
    if citations:
        st.markdown("### 📚 Sources")
        for idx, chunk in enumerate(citations, 1):
            with st.expander(f"📄 Source {idx} (score: {chunk.get('rerank_score', chunk.get('score', 'N/A')):.4f})"):
                st.markdown(f'<div class="source-card">{chunk["content"]}</div>', unsafe_allow_html=True)
                if "document_id" in chunk:
                    st.caption(f"Document ID: {chunk['document_id']}")
    else:
        st.info("No citations extracted from the answer.")

    # Optionally show full retrieved chunks (debug)
    with st.expander("🔍 Full retrieved chunks (for inspection)"):
        for i, chunk in enumerate(data.get("citations", []), 1):
            st.write(f"**Chunk {i}**")
            st.write(chunk["content"])
            st.write("---")

# ---------- FOOTER ----------
st.markdown(
    """
    <div class="footer">
        Built with ❤️ using FastAPI, PostgreSQL, Gemini, and Streamlit.
        <br>
        <a href="https://github.com/a-janjan/openks" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True,
)