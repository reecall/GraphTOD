import graphviz as gv
import argparse
from objects import RecipeMachine, DoctorMachine, RentCarMachine, HotelMachine, WorkerAgendaMachine
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())



def get_graph_dot(transitions_graph: dict, name: str):
    # # Create a Graphviz Digraph
    dot = gv.Digraph(comment=f"{name} graph")

    # Add nodes and edges based on the dictionary
    for state, transitions in transitions_graph.items():
        for action, next_state in transitions.items():
            dot.edge(state, next_state, label=action)
    return dot


def create_graph(transitions_graph: dict, name: str):
    # Create a Graphviz Digraph
    dot = get_graph_dot(transitions_graph, name)
    # Render the graph to a PNG file
    dot.render(f"{name}_graph_en", format="png", view=True)


if __name__ == "__main__":
    # Create a directed graph
    args = argparse.ArgumentParser()
    args.add_argument("-m", "--machine", type=str)
    args = args.parse_args()
    machines = {"recipe": RecipeMachine, "car": RentCarMachine, "doctor": DoctorMachine, "hotel": HotelMachine, "worker": WorkerAgendaMachine}
    if args.machine not in machines:
        raise ValueError(f"Machine {args.machine} not found")
    sm = machines[args.machine]()
    create_graph(sm.transitions_graph, sm.__class__.__name__)
