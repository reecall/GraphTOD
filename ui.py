import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

from objects.state_machine import StateMachine
from objects.AI_model import get_ai_model
from generate_conversations import generate_convs
from show_graph import get_graph_dot

from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
from streamlit_flow import streamlit_flow

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

    nodes = [
        StreamlitFlowNode(
            id="init_id",
            pos=(100, 100),
            data={"content": "InitialState"},
            node_type="input",
            source_position="right",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
            deletable=True,
        ),
        StreamlitFlowNode(
            "display_id",
            (350, 50),
            {"content": "DisplayHotels"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "display_details_id",
            (350, 50),
            {"content": "DisplayHotelDetails"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "ask_id",
            (350, 50),
            {"content": "AskPaymentInfo"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "ask_confirm_id",
            (350, 50),
            {"content": "AskPaymentConfirmation"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "pay_id",
            (350, 50),
            {"content": "PaymentAccepted"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "send_id",
            (350, 50),
            {"content": "SendInvoice"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "modify_id",
            (350, 50),
            {"content": "ModificationPossible"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "criteria_added_id",
            (350, 50),
            {"content": "OtherCriteriaAdded"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "answer_refund_id",
            (350, 50),
            {"content": "AnswerForRefund"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "details_refund_id",
            (350, 50),
            {"content": "DetailsRefundDecision"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "alt_compensation_id",
            (350, 50),
            {"content": "AlternativeCompensation"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "compensation_ok_id",
            (350, 50),
            {"content": "CompensationAccepted"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "compensation_notok_id",
            (350, 50),
            {"content": "CompensationRefused"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "booking_id",
            (350, 150),
            {"content": "BookingFound"},
            "default",
            "right",
            "left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
        StreamlitFlowNode(
            "end_id",
            (600, 100),
            {"content": "Stop"},
            "output",
            target_position="left",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
        ),
    ]

    edges = [
        StreamlitFlowEdge(
            "init_id-display_id",
            "init_id",
            "display_id",
            animated=True,
            label="search_hotels",
            label_show_bg=True,
            # marker_end={type: "arrow"},
        ),
        StreamlitFlowEdge(
            "init_id-booking_id",
            "init_id",
            "booking_id",
            animated=True,
            label="ask_cancelling_or_modifying_reservation",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "display_id-ask_id",
            "display_id",
            "ask_id",
            animated=True,
            label="select_hotel",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "display_id-display_id",
            "display_id",
            "display_id",
            animated=True,
            label="ask_for_more_hotels",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "display_id-display_details_id",
            "display_id",
            "display_details_id",
            animated=True,
            label="ask_for_details",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "display_details_id-ask_id",
            "display_details_id",
            "ask_id",
            animated=True,
            label="select_hotel",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "display_details_id-display_id",
            "display_details_id",
            "display_id",
            animated=True,
            label="ask_for_more_hotel",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "ask_id-ask_confirm_id",
            "ask_id",
            "ask_confirm_id",
            animated=True,
            label="check_payment_type",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "ask_confirm_id-pay_id",
            "ask_confirm_id",
            "pay_id",
            animated=True,
            label="process_payment",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "pay_id-send_id",
            "pay_id",
            "send_id",
            animated=True,
            label="request_invoice",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "pay_id-end_id",
            "pay_id",
            "end_id",
            animated=True,
            label="end",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "send_id-end_id",
            "send_id",
            "end_id",
            animated=True,
            label="end",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "booking_id-modify_id",
            "booking_id",
            "modify_id",
            animated=True,
            label="criteria_to_modify",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "booking_id-answer_refund_id",
            "booking_id",
            "answer_refund_id",
            animated=True,
            label="refund",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "modify_id-criteria_added_id",
            "modify_id",
            "criteria_added_id",
            animated=True,
            label="add_criteria",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "criteria_added_id-end_id",
            "criteria_added_id",
            "end_id",
            animated=True,
            label="end",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "answer_refund_id-details_refund_id",
            "answer_refund_id",
            "details_refund_id",
            animated=True,
            label="contest_refund_decision",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "answer_refund_id-end_id",
            "answer_refund_id",
            "end_id",
            animated=True,
            label="accept_decision",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "details_refund_id-end_id",
            "details_refund_id",
            "end_id",
            animated=True,
            label="accept_decision",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "details_refund_id-alt_compensation_id",
            "details_refund_id",
            "alt_compensation_id",
            animated=True,
            label="ask_for_another_compensation",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "alt_compensation_id-compensation_ok_id",
            "alt_compensation_id",
            "compensation_ok_id",
            animated=True,
            label="user_accepts",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "alt_compensation_id-compensation_notok_id",
            "alt_compensation_id",
            "compensation_notok_id",
            animated=True,
            label="user_refuses",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "compensation_ok_id-end_id",
            "compensation_ok_id",
            "end_id",
            animated=True,
            label="end",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "compensation_notok_id-alt_compensation_id",
            "compensation_notok_id",
            "alt_compensation_id",
            animated=True,
            label="negociate_compensation",
            label_show_bg=True,
        ),
        StreamlitFlowEdge(
            "compensation_notok_id-end_id",
            "compensation_notok_id",
            "end_id",
            animated=True,
            label="end",
            label_show_bg=True,
        ),
    ]

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
    )
    col1, col2 = st.columns(2)
    col1.metric("Nodes", len(new_state.nodes))
    col2.metric("Edges", len(new_state.edges))

    # st.write([new_state.asdict()])
    # st.write([dir(o) for o in new_state.edges])

    # st.write([o.id for o in new_state.nodes])
    # st.write([[o.label, o.source, str(o.target)] for o in new_state.edges])

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
    # st.write(json_edges)

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

    def increment_counter():
        st.session_state.count += 1

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

    launcheval_button = st.button(
        "Evaluate the generated conversations (GPU needed)",
        use_container_width=True,
        type="primary",
        key="launcheval_button",
        disabled=st.session_state.eval_disabled,
        on_click=click_eval_button,
    )

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
                # Convert the a list of dict to a jsonlines file
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
        counter_conv = st.button("Next conversation", on_click=increment_counter)
        st.session_state.eval_disabled = False

        # Show a conversation example
        st.markdown("---")
        r_col1, r_col2 = st.columns(2)

        with r_col1:
            st.subheader("Example of generated conversation")
            if len(st.session_state.conv_generated) > 1:
                if st.session_state.count >= len(st.session_state.conv_generated):
                    st.session_state.count = 0
            else:
                st.session_state.count = 0
            example_conv = st.session_state.conv_generated[st.session_state.count][
                "conversation"
            ]
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
                [conv["user"] for conv in st.session_state.conv_generated]
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
            users_df["age"] = pd.cut(users_df["age"], bins=age_bins, labels=age_labels)
            age_counts = users_df["age"].value_counts()
            plt.figure(figsize=(8, 6))
            plt.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%")
            plt.title("Age Distribution")
            plt.axis("equal")
            st.pyplot(plt)

        st.write("<center>", unsafe_allow_html=True)
        st.download_button(
            label="Download generated dataset as a jsonlines",
            data=st.session_state.conv_generated_jsonl,
            file_name="generated_conversations.jsonl",
            mime="application/json",
        )
        st.write("</center>", unsafe_allow_html=True)
