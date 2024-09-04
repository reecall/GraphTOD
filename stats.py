import json
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from objects import HotelMachine, RentCarMachine


# I want to write a function that extracts the node names from the tradesman machine
def extract_nodes(machine: dict):
    return set(machine.keys()), set(machine.values())


def create_adj_mat(states, machine):
    adj_matrix = {state: [0] * len(states) for state in states}

    # Mapping each transition to the adjacency matrix
    for state, transitions in machine.items():
        for _, target in transitions.items():
            col = states.index(target)
            adj_matrix[state][col] = 1

    return np.array([adj_matrix[state] for state in states])


def find_all_paths(adjacency_matrix, start, stop, max_depth=15):
    stack = [(start, [start])]
    all_paths = []

    while stack:
        current_node, path = stack.pop()

        if len(path) > max_depth:
            continue

        if current_node == stop:
            all_paths.append(path)
            continue

        for next_node in range(len(adjacency_matrix)):
            if adjacency_matrix[current_node][next_node] == 1:
                # Only add to stack if we haven't exceeded the max_depth or reached a cycle
                # if next_node not in path or next_node == stop:
                # print(next_node)
                stack.append((next_node, path + [next_node]))

    return all_paths


def assign_name_to_path(all_theory_paths, states):
    all_readable_paths = []
    for path in all_theory_paths:
        state_names = states
        readable_path = list(str(state_names[node]) for node in path)
        all_readable_paths.append(readable_path)
    return all_readable_paths


def open_jsonl_randompath(file):
    with open(file) as f:
        all_paths = []
        for line in f:
            path = []
            d = json.loads(line.rstrip("\n"))
            for rd in d["random_walk"]:
                path.append(rd[0])
            all_paths.append(path)
    return all_paths


def compare_paths(all_theory_paths, all_paths):
    tot = [elem for L in all_theory_paths for elem in L]
    tot2 = [elem for L in all_paths for elem in L]

    theory_path = Counter(tot)
    real_path = Counter(tot2)

    df = pd.DataFrame([theory_path, real_path], index=["all paths", "random walk"])
    df = df.transpose()

    total_theory_path = sum(theory_path.values())
    total_real_path = sum(real_path.values())
    theory_path = {
        key: (value / total_theory_path) * 100 for key, value in theory_path.items()
    }
    real_path = {
        key: (value / total_real_path) * 100 for key, value in real_path.items()
    }
    df2 = pd.DataFrame([theory_path, real_path], index=["all paths", "random walk"])

    df.plot(kind="bar")
    df2.plot(kind="bar")
    plt.tight_layout()  # to make sure that x-axis labels are always shown fully
    plt.show()


class StatConversations:
    def __init__(self, file, machine):
        self.randomwalk = []
        self.conversation = []
        self.nodes = []
        self.transitions = []
        self.machine = machine.transitions_graph
        with open(file) as f:
            for line in f:
                path = []
                convs = []
                nodes_n = []
                transitions_n = []
                d = json.loads(line.rstrip("\n"))
                for rd in d["random_walk"]:
                    path.append(rd)  # to access to Node rd[0] and action rd[1]
                    nodes_n.append(rd[0])
                    transitions_n.append(rd[1])
                self.nodes.append(nodes_n)
                self.transitions.append(transitions_n)
                for conv in d["conversation"]:
                    convs.append(conv)
                self.randomwalk.append(path)
                self.conversation.append(convs)

    def get_data(self):
        return self.randomwalk, self.conversation

    def mean_intents_per_conversation(self):
        # Explore the mean number of intents per conversation
        intents = []
        for conv in self.conversation:
            intents.append(len(conv))
        return np.mean(intents)

    def mean_unique_intent_per_conversation(self):
        intents = []
        for intent in self.randomwalk:
            L_intent = [x for n in intent for x in n]
            intents.append(len(set(L_intent)))
        return np.mean(intents)

    def n_conversation_per_intent(self):
        # Explore the number of conversation per intent
        a = extract_nodes(self.machine)
        intents = list(set(a[1]))
        nodes = a[0]
        concat = [intents, nodes]
        all = sum(concat, [])
        n_conversation = {key: 0 for key in all}
        for conv in self.randomwalk:
            intents_marked = []
            for elem in conv:
                if elem[0] in all and elem[0] not in intents_marked:
                    n_conversation[elem[0]] += 1
                    intents_marked.append(elem[0])
                if elem[1] in all and elem[1] not in intents_marked:
                    n_conversation[elem[1]] += 1
                    intents_marked.append(elem[1])
        return n_conversation

    def mean_number_of_goals_in_conversations(self):
        # A goal is the general intent of the conversation (book hotel, search hotel, book car, create quote, etc)
        # I want to know how many goals are in one conversation
        # If there is an intent called "other_x" it means that we are going to another goal
        goals = 0
        for conv in self.randomwalk:
            goals += 1
            for elem in conv:
                if "other" in elem[1]:
                    goals += 1
        return goals / len(self.randomwalk)


def print_dict_graphviz(intents_conv):
    # I want to use graphviz to print the results of a dictionary
    # I can use it print_conversation_per_intent
    fig, ax = plt.subplots()
    ax.bar(intents_conv.keys(), intents_conv.values())
    plt.xticks(rotation=45)
    plt.show()


def create_theoretical_paths_from(machine):
    a = extract_nodes(machine)[0]
    adj_bis = create_adj_mat(a, machine)

    start_index = 0  # Start
    stop_index = len(adj_bis) - 1  # Stop
    all_theory_paths = find_all_paths(adj_bis, start_index, stop_index)
    print(f"Total number of paths printed : {len(all_theory_paths)}")

    all_readable_paths = assign_name_to_path(all_theory_paths, a)
    return all_readable_paths


if __name__ == "__main__":
    hotels = StatConversations(
        "generated_conv/HotelMachine_simulated_conversation_2.jsonl", HotelMachine()
    )
    plot_intentperconv = hotels.n_conversation_per_intent()
    print(plot_intentperconv)
    print_dict_graphviz(plot_intentperconv)
    print(hotels.mean_number_of_goals_in_conversations())
    print(hotels.n_conversation_per_intent())

    car = StatConversations(
        "generated_conv/RentCarMachine_simulated_conversation.jsonl", RentCarMachine()
    )
    plot_intentperconv_car = car.n_conversation_per_intent()
    print_dict_graphviz(plot_intentperconv_car)
    print(car.mean_number_of_goals_in_conversations())
