import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Conversation reader",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.title("🗣️ Conversation reader")
    # upload a file in jsonl format
    uploaded_file = st.file_uploader("Upload your conversation file", type=["jsonl"])
if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    # read the file
    content = uploaded_file.getvalue()
    conversations = [
        json.loads(conv) for conv in content.decode("utf-8").split("\n") if conv
    ]
    with st.sidebar:
        num_samples = st.slider(
            "Number of conversation to generate", 1, len(conversations), 1
        )

    selected_conv = conversations[num_samples - 1]
    with st.sidebar:
        st.write(selected_conv["user"])

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        walk = [item for sublist in selected_conv["random_walk"] for item in sublist]
        for message, current_node_or_edge in zip(selected_conv["conversation"], walk):
            st.chat_message(message["role"]).write(f"{message["text"]} _({current_node_or_edge})_")
