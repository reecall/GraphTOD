from objects.state_machine import StateMachine


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

    def generate_conversation(self, model, seed: int):
        history = []
        sm = self.state_machine
        rd_walk = self.state_machine.get_random_walk(seed=seed)
        step = 0
        while True:
            history.append(
                {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
            )

            next_transition = rd_walk[step][1] if step < len(rd_walk) else "stop"
            detailed_intent = model.invoke(
                [
                    ("system", "You are an agent expert in state-transition graphs"),
                    (
                        "user",
                        f"Explain in few words the user intent that hides behind this transition name : {next_transition}",
                    ),
                ],
            ).content

            prompt = [
                (
                    "system",
                    (
                        "You should act as a user interacting with an agent. "
                        f"Here is the user properties : {str(self)}.\n"
                        "Your goal is to generate the next user sentence of a dialog between a human and a cooking agent, based on the intent of the user. "
                        "To generate the next user input, you must follow the conversation flow and what the agent is asking you to do. "
                        "For context, here is the history of the conversation, where you are the user:\n"
                        f"{sm.history_to_string()}\n"
                        "Your generation need to be short, concise, look like a line of dialog, as someone speaking to a home assistant. "
                        "Your generation must look like a human transcription, and not like a machine generated text. "
                        "If the agent asks you to choose among multiple choices, you should choose one of them, and tell the agent your choice.\n"
                        "Return just the next sentence to say to the agent, and nothing else."
                    ),
                ),
                (
                    "user",
                    f'Here is the intent of the user : {detailed_intent}.\n Based on this, what should the user answer to "{sm.history[-1][1]}"?',
                ),
            ]

            user_input = model.invoke(
                prompt,
                temperature=0.3,
            ).content

            output = sm.get_response(user_input)
            history.append(
                {"role": "user", "text": user_input, "transition": output["transition"]}
            )
            step += 1
            if sm.state == "stop":
                history.append(
                    {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
                )
                break
        return history, rd_walk
