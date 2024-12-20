from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import json
import objects.hotel_machine as hotel_machine


def json_to_streamlit_flow(json_data):
    nodes = []
    edges = []
    for node in json_data.keys():
        st = StreamlitFlowNode(
            id=node,
            pos=(350, 50),
            data={"content": node},
            source_position="right",
            target_position="left",
            node_type="default",
            selected=True,
            dragging=True,
            draggable=True,
            selectable=True,
            deletable=True,
        )
        if node == "InitialState":
            st.node_type = "input"
        nodes.append(st)
        # nodes[0].style = {
        #     "backgroundColor": "red",
        #     "fontWeight": 900,
        # }

        for edge in json_data[node].keys():
            edge_id = node + "-" + json_data[node][edge]
            edges.append(
                StreamlitFlowEdge(
                    id=edge_id,
                    source=node,
                    target=json_data[node][edge],
                    label=edge,
                    animated=True,
                    label_show_bg=True,
                    marker_end={"type": "arrow"},
                    deletable=True,
                    # label_bg_style={"stroke": "red", "fill": "white"},
                )
            )

    return nodes, edges


# graph = hotel_machine.HotelMachine()
# graph_st = json_to_streamlit_flow(graph.to_json()["transitions_graph"])
# print(graph_st[0][0].style)
# for n in graph_st[0]:
#     n.style = {"backgroundColor": "green", "fontWeight": 900}
#     break
# print(graph_st[0][0].style)


def highlight_conv_path(flowdata, conv):
    if "conversation" in conv:
        conversation = conv["conversation"]
        for s in conversation:
            if "state" in s:
                state = s["state"]
                modified = False
                for i in range(len(flowdata.nodes)):
                    if flowdata.nodes[i].data["content"] == state:
                        flowdata.nodes[i].style = {
                            "backgroundColor": "orange",
                            "fontWeight": 900,
                        }
                        modified = True
                if modified:
                    for i in range(len(flowdata.edges)):
                        if flowdata.edges[i].source == state:
                            flowdata.edges[i].style = {
                                "lineColor": "orange",
                                "lineWidth": 3,
                            }
    return flowdata


# path = highlight_conv_path(graph_st)
