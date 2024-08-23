import streamlit as st
import json
import pandas as pd
from objects.AI_model import get_ai_model


# Function to generate dataset from state transition graph
def generate_dataset(state_graph):
    pass


st.set_page_config(
    page_title="Conversation generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit app
st.title("OpenAI or Azure OpenAI State Transition Dataset Generator")

# API Key input
with st.sidebar:
    # add a two button for openai and azure openai
    selected_provider = st.radio(
        "👇 First, select a provider",
        [("OpenAI", "openai"), ("Azure OpenAI", "azure_openai")],
        horizontal=True,
        format_func=lambda x: x[0],
    )[1]
    model_name = st.text_input("Enter the name of the model you want to use")
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    if selected_provider == "azure_openai":
        deployment_endpoint = st.text_input("Enter your Deployment Endpoint", "")

if (api_key and model_name and selected_provider == "openai") or (
    api_key
    and deployment_endpoint
    and model_name
    and selected_provider == "azure_openai"
):
    if selected_provider == "openai":
        deployment_endpoint = None

    get_ai_model().set_model(
        type=selected_provider,
        model_name=model_name,
        api_key=api_key,
        endpoint=deployment_endpoint,
    )
    col1, col2 = st.columns(2)

    with col1:
        # JSON input for state transition graph
        json_input = st.text_area(
            "Enter your state transition graph in JSON format",
            help="Enter here your state-transition graph formatted as explained in the readme.",
        )

    with col2:
        if json_input:
            # visualize json
            st.json(json_input)

    initial_sentence = st.text_input(
        "Enter your initial sentence",
        placeholder="Hello my name is John, how can I help you ?",
    )

    # slider to generate from 1 to 1000 samples
    num_samples = st.slider("Number of conversation to generate", 1, 1000, 100)

    # add a panel where you can assigne transition to api endpoint
    with st.expander("Function calling assignation"):
        st.data_editor(
            pd.DataFrame(columns=["Transition", "API Endpoint"]),
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )

    if st.button("Generate conversation dataset", use_container_width=True):
        try:
            state_graph = json.loads(json_input)
            df = generate_dataset(state_graph)
            st.write(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Dataset as CSV",
                data=csv,
                file_name="state_transition_dataset.csv",
                mime="text/csv",
            )
        except json.JSONDecodeError:
            st.error("Invalid JSON input. Please correct it and try again.")
