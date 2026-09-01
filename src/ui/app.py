import streamlit as st
import requests

st.title("Open Knowledge Search & RAG")

query = st.text_input("Ask a question")
if query:
    # Call your FastAPI /answer endpoint
    response = requests.post("http://localhost:8000/answer", json={"query": query})
    if response.status_code == 200:
        data = response.json()
        st.write("**Answer:**", data["answer"])
        st.write("**Grounded?**", data.get("grounded", "N/A"))
        if "citations" in data and data["citations"]:
            st.write("**Sources:**")
            for idx, chunk in enumerate(data["citations"]):
                with st.expander(f"Source {idx+1}"):
                    st.write(chunk["content"])

    else:
        st.error("Error calling API")
