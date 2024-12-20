import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

from objects.state_machine import StateMachine
from objects.AI_model import get_ai_model
from generate_conversations import generate_convs
from show_graph import get_graph_dot
from utils_streamlit import json_to_streamlit_flow, highlight_conv_path

from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
from streamlit_flow import streamlit_flow

import objects.hotel_machine as hotel_machine
import objects.doctor_machine as doctor_machine
import objects.recipe_machine as recipe_machine
import objects.rent_car_machine as rent_car_machine
import objects.worker_agenda_machine as worker_agenda_machine

use_unieval = False

if use_unieval:
    import torch
    from unieval.eval_conv import unieval_eval
# if torch.cuda.is_available():
# use_unieval = True

st.set_page_config(
    page_title="Conversation generator",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit app
st.title("🗣️ Conversation dataset generator")


st.write("Create a task oriented dialogue conversation dataset using a state machine.")
st.write("Modify the example below or create your own graph.")
st.write(
    "Right click to add nodes, and then drag and drop to connect them. Right click on nodes or edges to modify their label or delete them. The conversation flow goes from left to right."
)

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

    # TODO: add a button to charge the graph and change between the different state machines
    # TODO: add a button to empty the graph window
    graph = hotel_machine.HotelMachine()
    nodes, edges = json_to_streamlit_flow(graph.to_json()["transitions_graph"])
    new_state = streamlit_flow(
        "fully_interactive_flow",
        StreamlitFlowState(
            nodes, edges
        ),  # Start with an empty state, or with some pre-initialized state
        fit_view=True,
        show_controls=True,
        allow_new_edges=True,
        animate_new_edges=True,
        layout=TreeLayout("right"),
        enable_pane_menu=True,
        enable_edge_menu=True,
        enable_node_menu=True,
        show_minimap=True,
        hide_watermark=True,
    )
    col1, col2 = st.columns(2)
    col1.metric("Nodes", len(new_state.nodes))
    col2.metric("Edges", len(new_state.edges))

    def extract_states_edges(edges, nodes):
        states = {}
        val = {node.id: node.data["content"] for node in nodes}

        list_edges = [o for o in edges]
        for edge in list_edges:
            source = val[edge.source]
            target = val[edge.target]
            if source not in states:
                states[source] = {}

            states[source][edge.label] = target
        return states

    json_edges = extract_states_edges(new_state.edges, new_state.nodes)

    initial_sentence = st.text_input(
        "Enter your initial sentence",
        "Hello, I'm your assistant, how can I help you ?",
        placeholder="Hello my name is John, how can I help you ?",
    )

    custom_api_url = st.text_input(
        "Enter the custom API URL",
        placeholder="https://my_custom_api.com/",
    )

    # slider to generate from 1 to 1000 samples
    num_samples = st.slider("Number of conversation to generate", 1, 1000, 100)

    # add a panel where you can assign transition to api endpoint

    df = pd.DataFrame(
        {
            "Transition": ["select_hotel", "search_hotels", "ask_for_more_hotels"],
            "API Endpoint": ["select_i", "/hotel/search", "/hotel/search"],
        }
    )

    with st.expander("Function calling settings"):
        function_calling_df = st.data_editor(
            # pd.DataFrame(columns=["Transition", "API Endpoint"]),
            df,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
        )

    # Convert function calling to a json "transition": "api_endpoint"
    function_calling = function_calling_df.dropna().to_dict(orient="records")
    function_calling = {
        item["Transition"]: item["API Endpoint"] for item in function_calling
    }

    if "count" not in st.session_state:
        st.session_state.count = 0

    if "eval_disabled" not in st.session_state:
        st.session_state.eval_disabled = True
    if "eval_button" not in st.session_state:
        st.session_state.eval_button = False

    if "gen_clicked" not in st.session_state:
        st.session_state.gen_clicked = False

    if "conv_generated" not in st.session_state:
        st.session_state.conv_generated = ""

    if "conv_generated_jsonl" not in st.session_state:
        st.session_state.conv_generated_jsonl = ""

    if "highlighted_flow" not in st.session_state:
        st.session_state.highlighted_flow = ""

    def increment_counter():
        st.session_state.count += 1
        st.rerun()

    def reset_counter():
        st.session_state.count = 0

    def click_button():
        st.session_state.gen_clicked = True

    def click_eval_button():
        st.session_state.eval_button = True

    generate_button = st.button(
        "Generate conversation dataset",
        use_container_width=True,
        type="primary",
        key="generate_button",
        on_click=click_button,
    )

    # launcheval_button = st.button(
    #     "Evaluate the generated conversations (GPU needed)",
    #     use_container_width=True,
    #     type="primary",
    #     key="launcheval_button",
    #     disabled=st.session_state.eval_disabled,
    #     on_click=click_eval_button,
    # )

    config_data = {
        "transitions_graph": json_edges if json_edges else "",
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

    if st.session_state.gen_clicked:
        try:
            state_graph = json_edges

            sm = StateMachine(
                state_graph,
                function_calling,
                initial_sentence=initial_sentence,
                api_adress=custom_api_url,
            )
            with st.spinner("Generating conversations..."):
                generated_conversations = generate_convs(sm, num_samples)
                # Convert the list of dict to a jsonlines file
                generated_conversations_jsonl = "\n".join(
                    [
                        json.dumps(conv, ensure_ascii=False)
                        for conv in generated_conversations
                    ]
                )
            st.session_state.conv_generated = generated_conversations
            st.session_state.conv_generated_jsonl = generated_conversations_jsonl
            st.session_state.gen_clicked = False
            st.session_state.eval_disabled = False
        except json.JSONDecodeError:
            st.error("Invalid JSON input. Please correct it and try again.")

    if use_unieval:
        if st.session_state.eval_button:
            # Show Unieval evaluation of those conversations
            st.markdown("---")
            st.subheader("Evaluate the generated conversations (GPU needed)")
            eval_convs = unieval_eval(
                st.session_state.conv_generated_jsonl,
                ["naturalness", "coherence", "understandability"],
                mode="full",
                type="graphtod",
            )
            st.write(eval_convs)

    if st.session_state.conv_generated:
        st.write("Conversation number {}".format(st.session_state.count + 1))
        if len(st.session_state.conv_generated) == st.session_state.count:
            st.session_state.count = 0
            counter_conv = st.button("Next conversation", on_click=reset_counter)
        else:
            counter_conv = st.button("Next conversation", on_click=increment_counter)

        st.session_state.eval_disabled = True

        if len(st.session_state.conv_generated) > 1:
            if st.session_state.count >= len(st.session_state.conv_generated):
                st.session_state.count = 0
        else:
            st.session_state.count = 0

        st.markdown("---")
        r_col1 = st.columns(1)[0]
        with r_col1:
            flow = highlight_conv_path(
                new_state,
                st.session_state.conv_generated[st.session_state.count],
            )

            highlight_flow = streamlit_flow(
                "highlighted_flow",
                StreamlitFlowState(
                    flow.nodes, flow.edges
                ),  # Start with an empty state, or with some pre-initialized state
                fit_view=True,
                # show_controls=True,
                # allow_new_edges=True,
                # animate_new_edges=True,
                layout=TreeLayout("right"),
                # enable_pane_menu=True,
                # enable_edge_menu=True,
                # enable_node_menu=True,
                # show_minimap=True,
                hide_watermark=True,
            )

        # Show a conversation example
        st.markdown("---")
        r_col1, r_col2 = st.columns(2)

        with r_col1:
            st.subheader("Example of generated conversation")
            example_conv = st.session_state.conv_generated[st.session_state.count][
                "conversation"
            ]

            st.write(
                " <br />".join(
                    [f"[{line['role']}]: {line['text']}" for line in example_conv]
                ),
                unsafe_allow_html=True,
            )

        # with r_col2:
        #     # make stats about users
        #     st.subheader("Stats about generated conversations persona")
        #     users_df = pd.DataFrame(
        #         [conv["user"] for conv in st.session_state.conv_generated]
        #     )
        #     # Create a pie chart for gender distribution
        #     gender_counts = users_df["gender"].value_counts()
        #     plt.figure(figsize=(8, 6))
        #     plt.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%")
        #     plt.title("Gender Distribution")
        #     plt.axis("equal")
        #     st.pyplot(plt)
        #     # Create a pie chart for age distribution
        #     # 18/24, 25/34, 35/49, 50/64, et 65 et plus
        #     age_bins = [18, 25, 35, 50, 65, 100]
        #     age_labels = ["18-24", "25-34", "35-49", "50-64", "65+"]
        #     users_df["age"] = pd.cut(users_df["age"], bins=age_bins, labels=age_labels)
        #     age_counts = users_df["age"].value_counts()
        #     plt.figure(figsize=(8, 6))
        #     plt.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%")
        #     plt.title("Age Distribution")
        #     plt.axis("equal")
        #     st.pyplot(plt)
        #
        st.write("<center>", unsafe_allow_html=True)
        st.download_button(
            label="Download generated dataset as a jsonlines",
            data=st.session_state.conv_generated_jsonl,
            file_name="generated_conversations.jsonl",
            mime="application/json",
        )
        st.write("</center>", unsafe_allow_html=True)
