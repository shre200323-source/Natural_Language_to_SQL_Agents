"""
Streamlit frontend for the NL -> SQL agent. It only calls the FastAPI backend (/ask, /health).

Run from the nl_sql_agent folder:
    uvicorn app.main:app --reload             (terminal 1)
    streamlit run frontend/streamlit_app.py   (terminal 2)
"""
import ast

import pandas as pd
import requests
import streamlit as st

API_URL = "http://localhost:8000"

EXAMPLES = [
    "How many customers are there in each city?",
    "What products did Bob buy?",
    "Total revenue by product category",
    "Which customer spent the most?",
    "List all pending or processing orders",
]

st.set_page_config(page_title="Sales SQL Assistant", page_icon="🧮", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []


def ask_api(question):
    response = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=180)
    response.raise_for_status()
    return response.json()


def show_result(result):
    st.markdown(result["answer"])
    st.caption(f"Attempts: {result.get('attempts', '?')}")

    table_tab, sql_tab = st.tabs(["Table", "SQL"])
    with table_tab:
        if result.get("query_result"):
            data = ast.literal_eval(result["query_result"])   # {"columns": [...], "rows": [...]}
            df = pd.DataFrame(data["rows"], columns=data["columns"])
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info(result.get("error") or "No rows returned.")
    with sql_tab:
        st.code(result.get("sql_query") or "-- no SQL generated", language="sql")


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Sales SQL Assistant")
    try:
        requests.get(f"{API_URL}/health", timeout=3).raise_for_status()
        st.success("API connected")
    except requests.exceptions.RequestException:
        st.error(f"API not reachable at {API_URL}.\nStart it with: uvicorn app.main:app --reload")

    st.subheader("Example questions")
    clicked = None
    for example in EXAMPLES:
        if st.button(example, use_container_width=True):
            clicked = example

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- chat ----------------
st.title("🧮 Ask your sales database")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        elif "result" in message:
            show_result(message["result"])
        else:
            st.error(message["content"])

question = st.chat_input("Ask a question about customers, products or orders") or clicked

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL..."):
            try:
                result = ask_api(question)
                show_result(result)
                st.session_state.messages.append({"role": "assistant", "result": result})
            except requests.exceptions.RequestException as exc:
                st.error(f"Request failed: {exc}")
                st.session_state.messages.append({"role": "assistant", "content": f"Request failed: {exc}"})
