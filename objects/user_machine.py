import random as rd

from objects.state_machine import StateMachine
from objects.AI_model import AIModel


class UserMachine:
    @classmethod
    def from_json(cls, json: dict):
        return cls(
            name=json.get("name"),
            age=json.get("age"),
            gender=json.get("gender"),
            informations=json.get("informations"),
        )

    def __init__(
        self,
        name: str,
        age: int,
        gender: str,
        informations: dict = [],
        state_machine: StateMachine = None,
    ):
        self.name = name
        self.age = age
        self.gender = gender
        self.informations = informations
        self.history = []
        self.state_machine = state_machine

    def __str__(self):
        return f"User(name={self.name}, age={self.age}, gender={self.gender}, informations={self.informations})"

    def set_state_machine(self, state_machine: StateMachine):
        self.state_machine = state_machine

    def to_json(self):
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "informations": self.informations,
        }

    def generate_conversation(self, model: AIModel, graph_description: str, seed: int):
        history = []
        rd.seed(seed)
        sm = self.state_machine
        walk = []
        while True:
            history.append(
                {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
            )

            next_transition = rd.choice(sm.get_next_transitions())
            other_transitions = sm.get_next_transitions()
            other_transitions.remove(next_transition)

            walk.append((sm.state, next_transition))

            prompt = [
                (
                    "system",
                    (
                        "You should act as a user interacting with an agent. "
                        f"Here is the user properties : {str(self)}.\n"
                        f"Here is a summary of the graph : {graph_description}\n"
                        "Your goal is to generate the next user sentence of a dialog between a human and an agent, based on the intent of the user and the last agent sentence. "
                        "To generate the next user input, you must follow the conversation flow, what the agent is asking and the user intent. "
                        "For context, here is the history of the conversation, where you are the user:\n"
                        f"{sm.history_to_string()}\n"
                        "Your generation need to be short, concise, look like a line of dialog, as someone speaking to a home assistant. "
                        "Your generation must look like a human transcription, and not like a machine generated text. "
                        "If the agent asks you to choose among multiple choices, you should choose one of them, and tell the agent your choice.\n"
                        f"Return just the next sentence to say to the agent, and nothing else."
                    ),
                ),
                (
                    "user",
                    f'Here is the intent of the user : {next_transition}.\n Based on this, generate a response to "{sm.history[-1][1]}", which is the agent\'s last sentence, reflecting the intent of the user.',
                ),
            ]

            user_input = (
                model()
                .invoke(
                    prompt,
                    temperature=0.2,
                )
                .content
            )

            output = sm.get_response(user_input)
            if output["transition"] != next_transition:
                print(
                    f"Error: the transition generated by the model is not the same as the transition of the state machine.\n"
                    f"Generated transition: {output['transition']}, expected transition: {next_transition}"
                )
                print(f"Machine output: {sm.history[-3][1]}")
                print(f"User input: {user_input}")
                print(f"State machine state: {sm.state}")
                print()

            history.append(
                {"role": "user", "text": user_input, "transition": output["transition"]}
            )
            if sm.state == "Stop":
                history.append(
                    {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
                )
                break
        return history, walk