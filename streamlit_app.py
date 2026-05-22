import streamlit as st
import json
from snowflake.snowpark.context import get_active_session

session = get_active_session()

SEMANTIC_MODEL = "@DBADMIN.ASSETS.MODEL_STAGE/finops_model.yaml"

def call_cortex_analyst(prompt):
    import requests as req
    rest = session.connection._rest
    url = f"https://{rest._host}:443/api/v2/cortex/analyst/message"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f'Snowflake Token="{rest.token}"',
    }
    analyst_messages = []
    expected_role = "user"
    for msg in st.session_state.messages:
        if msg["role"] == expected_role:
            if msg["role"] == "user":
                analyst_messages.append({"role": "user", "content": [{"type": "text", "text": msg["content"][0]["text"]}]})expected_role = "analyst"
            elif msg["role"] == "analyst":
                analyst_messages.append({"role": "analyst", "content": msg["content"]})
                expected_role = "user"
    if analyst_messages and analyst_messages[-1]["role"] == "user":
        analyst_messages.pop()
    analyst_messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
    request_body = {
        "messages": analyst_messages,
        "semantic_model_file": SEMANTIC_MODEL,
    }
    resp = req.post(url, json=request_body, headers=headers)
    if resp.status_code < 400:
        return resp.json()
    else:
        raise Exception(f"Status {resp.status_code}: {resp.text}")

st.title("Snowflake Intelligence Agent")
st.caption("Ask me about warehouse efficiency, credit burn, or optimization tips.")

if "messages" not in st.session_state or "reset" not in st.session_state:
    st.session_state.messages = []
    st.session_state.reset = True

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"][0]["text"])
        else:
            for item in msg["content"]:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "sql":
                    with st.expander("SQL Query", expanded=False):
                        st.code(item["statement"], language="sql")
                    with st.expander("Results", expanded=True):
                        df = session.sql(item["statement"]).to_pandas()
                        st.dataframe(df)

if prompt := st.chat_input("Ask about costs..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_cortex_analyst(prompt)
            content = response["message"]["content"]
            st.session_state.messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
            st.session_state.messages.append({"role": "analyst", "content": content})
            for item in content:
                if item["type"] == "text":
                    st.markdown(item["text"])
                elif item["type"] == "sql":
                    with st.expander("SQL Query", expanded=False):
                        st.code(item["statement"], language="sql")
                    with st.expander("Results", expanded=True):
                        df = session.sql(item["statement"]).to_pandas()
                        st.dataframe(df)
