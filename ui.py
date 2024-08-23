import streamlit as st
import json
import pandas as pd

from objects.state_machine import StateMachine
from objects.AI_model import get_ai_model
from generate_conversations import generate_convs


st.set_page_config(
    page_title="Conversation generator",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit app
st.title("🗣️ Conversation dataset generator")

# API Key input
with st.sidebar:
    st.title("Conversation generator")
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

    # add a markdown delimiter
    st.markdown("---")

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
            height=500,
        )

    with col2:
        if json_input:
            # visualize json
            st.json(json_input)

    initial_sentence = st.text_input(
        "Enter your initial sentence",
        placeholder="Hello my name is John, how can I help you ?",
    )

    custom_api_url = st.text_input(
        "Enter the custom API URL",
        placeholder="https://my_custom_api.com/",
    )

    # slider to generate from 1 to 1000 samples
    num_samples = st.slider("Number of conversation to generate", 1, 1000, 100)

    # add a panel where you can assigne transition to api endpoint
    with st.expander("Function calling settings"):
        function_calling_df = st.data_editor(
            pd.DataFrame(columns=["Transition", "API Endpoint"]),
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )

    # Convert function calling to a json "transition": "api_endpoint"
    function_calling = function_calling_df.dropna().to_dict(orient="records")
    function_calling = {
        item["Transition"]: item["API Endpoint"] for item in function_calling
    }

    generate_button = st.button(
        "Generate conversation dataset",
        use_container_width=True,
        type="primary",
        key="generate_button",
    )

    config_data = {
        "transitions_graph": json.loads(json_input) if json_input else "",
        "function_call": function_calling,
        "datafile": "",
        "initial_sentence": initial_sentence,
        "api_adress": custom_api_url,
    }
    with st.sidebar:
        st.download_button(
            "Download json config",
            data=json.dumps(config_data, indent=4, ensure_ascii=False),
            use_container_width=True,
            file_name="graph_config.json",
            mime="application/json",
        )

    if generate_button:
        try:
            state_graph = json.loads(json_input)

            sm = StateMachine(
                state_graph,
                function_calling,
                initial_sentence=initial_sentence,
                api_adress=custom_api_url,
            )
            with st.spinner("Generating conversations..."):
                generated_conversations = generate_convs(sm, num_samples)
                # Convert the a list of dict to a jsonlines file
                generated_conversations_jsonl = "\n".join(
                    [
                        json.dumps(conv, ensure_ascii=False)
                        for conv in generated_conversations
                    ]
                )

            # Show on example of conversation
            st.markdown("---")
            st.subheader("Example of generated conversation")
            example_conv = generated_conversations[0]["conversation"]
            st.write(
                " <br />".join(
                    [f"[{line['role']}]: {line['text']}" for line in example_conv]
                ),
                unsafe_allow_html=True,
            )

            st.download_button(
                label="Download generated dataset as a jsonlines",
                data=generated_conversations_jsonl,
                file_name="generated_conversations.jsonl",
                mime="application/json",
            )
        except json.JSONDecodeError:
            st.error("Invalid JSON input. Please correct it and try again.")
