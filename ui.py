import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

from objects.state_machine import StateMachine
from objects.AI_model import get_ai_model
from generate_conversations import generate_convs
from show_graph import get_graph_dot

from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
from streamlit_flow import streamlit_flow

default_graph = {
    "InitialState": {
        "search_hotels": "DisplayHotels",
        "ask_cancelling_or_modifying_reservation": "BookingFound",
    },
    "DisplayHotels": {
        "ask_for_more_hotels": "DisplayHotels",
        "select_hotel": "AskPaymentInfo",
        "ask_for_details": "DisplayHotelDetails",
    },
    "DisplayHotelDetails": {
        "select_hotel": "AskPaymentInfo",
        "ask_for_more_hotel": "DisplayHotels",
    },
    "AskPaymentInfo": {"check_payment_type": "AskPaymentConfirmation"},
    "AskPaymentConfirmation": {"process_payment": "PaymentAccepted"},
    "PaymentAccepted": {"request_invoice": "SendInvoice", "end": "Stop"},
    "SendInvoice": {"end": "Stop"},
    "BookingFound": {
        "criteria_to_modify": "ModificationPossible",
        "refund": "AnswerForRefund",
    },
    "ModificationPossible": {"add_criteria": "OtherCriteriaAdded"},
    "OtherCriteriaAdded": {"end": "Stop"},
    "AnswerForRefund": {
        "contest_refund_decision": "DetailsRefundDecision",
        "accept_decision": "Stop",
    },
    "DetailsRefundDecision": {"accept_decision": "Stop"},
    "Stop": {},
}


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
        # Create a switch button to choose between json visualisation or graph visualisation

        # JSON input for state transition graph
        json_input = st.text_area(
            "Enter your state transition graph in JSON format",
            json.dumps(default_graph, indent=4, ensure_ascii=False),
            help="Enter here your state-transition graph formatted as explained in the readme.",
            height=500,
        )

    with col2:
        see_graph_toggle = st.toggle("Visualize the graph", False)
        if json_input:
            if see_graph_toggle:
                # visualize graph
                graph_dot = get_graph_dot(json.loads(json_input), "Conversation")
                st.graphviz_chart(graph_dot)
            else:
                # visualize json
                st.json(json_input)

    new_state = streamlit_flow(
        "fully_interactive_flow",
        StreamlitFlowState(
            [], []
        ),  # Start with an empty state, or with some pre-initialized state
        fit_view=True,
        show_controls=True,
        allow_new_edges=True,
        animate_new_edges=True,
        layout=TreeLayout("right"),
        enable_pane_menu=True,
        enable_edge_menu=True,
        enable_node_menu=True,
    )
    col1, col2 = st.columns(2)
    col1.metric("Nodes", len(new_state.nodes))
    col2.metric("Edges", len(new_state.edges))

    # st.write(new_state.nodes)
    # st.write(new_state.edges)

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

            # # Show Unieval evaluation of those conversations
            # st.markdown("---")
            # st.subheader("Evaluate the generated conversations")
            # eval_convs = unieval_eval(
            #     generated_conversations_jsonl,
            #     ["naturalness", "coherence", "understandability"],
            #     mode="full",
            #     type="graphtod",
            # )
            # st.write(eval_convs)

            # Show on example of conversation
            st.markdown("---")
            r_col1, r_col2 = st.columns(2)
            with r_col1:

                st.subheader("Example of generated conversation")
                example_conv = generated_conversations[0]["conversation"]
                st.write(
                    " <br />".join(
                        [f"[{line['role']}]: {line['text']}" for line in example_conv]
                    ),
                    unsafe_allow_html=True,
                )

            with r_col2:
                # make stats about users
                st.subheader("Stats about generated conversations persona")
                users_df = pd.DataFrame(
                    [conv["user"] for conv in generated_conversations]
                )
                # Create a pie chart for gender distribution
                gender_counts = users_df["gender"].value_counts()
                plt.figure(figsize=(8, 6))
                plt.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%")
                plt.title("Gender Distribution")
                plt.axis("equal")
                st.pyplot(plt)
                # Create a pie chart for age distribution
                # 18/24, 25/34, 35/49, 50/64, et 65 et plus
                age_bins = [18, 25, 35, 50, 65, 100]
                age_labels = ["18-24", "25-34", "35-49", "50-64", "65+"]
                users_df["age"] = pd.cut(
                    users_df["age"], bins=age_bins, labels=age_labels
                )
                age_counts = users_df["age"].value_counts()
                plt.figure(figsize=(8, 6))
                plt.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%")
                plt.title("Age Distribution")
                plt.axis("equal")
                st.pyplot(plt)

            st.write("<center>", unsafe_allow_html=True)
            st.download_button(
                label="Download generated dataset as a jsonlines",
                data=generated_conversations_jsonl,
                file_name="generated_conversations.jsonl",
                mime="application/json",
            )
            st.write("</center>", unsafe_allow_html=True)
        except json.JSONDecodeError:
            st.error("Invalid JSON input. Please correct it and try again.")
