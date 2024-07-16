import json
from reellm import get_llm, get_embedding, ModelName


class StateMachine:
    def __init__(
        self,
        transitions_graph,
        initial_state,
        function_call,
        initial_sentence="Hello ! What can I do for you ?",
        DEBUG=False,
    ):
        self.state = initial_state
        self.transitions_graph = transitions_graph
        self.history = [("assistant", initial_sentence)]
        self.function_call = function_call
        self.knowledge = {}
        self.embedder = get_embedding(ModelName.EMBEDDING_LARGE)
        self.llm = get_llm(ModelName.GPT_4_O)
        self.DEBUG = DEBUG

    def __str__(self):
        return f"StateMachine(state={self.state})"

    def to_json(self):
        return {
            "state": self.state,
            "transitions_graph": self.transitions_graph,
        }

    def history_to_string(self):
        return "\n".join([f"{role}: {sentence}" for role, sentence in self.history])

    def get_response(self, input_text):
        # understand what's the transition ; then apply the transition ; then return the response
        transition_prompt = (
            "You're a agent specialized in state transition graph. "
            "You should act as an agent, based on the user input, the current state and the transitions graph. "
            "You should return the transition that suit the best following the user input as a json. "
            "Use elements from your context knowledge for your answer when you think it's relevant. "
            "Here is the information about the history of the conversation:\n"
            f"{self.history_to_string()}\n"
            "Here is all the transitions you can take, based on the current state :\n"
            f"{self.transitions_graph[self.state].keys()}\n"
            "Pick only a transition listed above, or return the transition 'none' if you think there is no transition corresponding. "
            "If you think that's the end of the conversation, return the transition 'stop'. "
            "Here is what you know in your context knowledge:\n"
            f"{self.knowledge}\n"
            "Predicte just the transition, and nothing else, as : {'transition': 'transition_name'}"
        )
        transition = self.llm.invoke(
            [("system", transition_prompt), ("user", input_text)],
            temperature=0,
            response_format={"type": "json_object"},
        ).content
        try:
            transition = json.loads(transition)["transition"]
        except KeyError:
            raise ValueError(
                f"Invalid transition format. Expected a json object with a 'transition' key, got {transition}"
                + "\n"
                + self.history_to_string()
            )
        if self.DEBUG:
            print(f"Transition: {transition}")
        self.transition(transition, input_text)

        if transition == "none":
            next_sentence = (
                "You're a agent specialized in state transition graph. "
                "You should act as an agent, based on the user input, the current state and the transitions graph. "
                "You should return the next sentence to say to the user, knowing that you didn't understand the user input, and that you can't handle such asking."
                "The sentence should be short and look like oral language."
                "Here is the information about the history of the conversation:\n"
                f"{self.history_to_string()}\n"
                "You need to inspire you from the state name to generate the next sentence. "
                "Do not forget to be polite and helpful."
            )
        elif transition == "stop":
            next_sentence = (
                "You're a agent specialized in state transition graph. "
                "You should act as an agent, based on the user input, the current state and the transitions graph. "
                "You should return the next sentence to say to the user, knowing that it's the end of the conversation."
                "The sentence should be short and look like oral language."
                "Insert elements in your context knowledge for your answer when you think it's relevant. "
                "Here is what you know in your context :\n"
                f"{self.knowledge}"
                f"Your sentence must correspond to the state '{self.state}'\n"
                "Here is the information about the history of the conversation:\n"
                f"{self.history_to_string()}\n"
                "You need to inspire you from the state name to generate the next sentence. "
                "Do not forget to be polite and helpful."
            )
        else:
            next_sentence = (
                "You're a agent specialized in state transition graph. "
                "You should act as an agent, based on the user input, the current state and the transitions graph. "
                "You should return the next sentence to say to the user."
                "The sentence should be short and look like oral language."
                "Insert elements in your context knowledge for your answer when you think it's relevant. "
                "Here is what you know in your context :\n"
                f"{self.knowledge}"
                f"Your sentence must correspond to the state '{self.state}'\n"
                "Here is the information about the history of the conversation:\n"
                f"{self.history_to_string()}\n"
                "You need to inspire you from the state name to generate the next sentence, and use all the knowledge you can. "
                "Do not forget to be polite and helpful."
            )

        sentence_to_say = self.llm.invoke(
            [("system", next_sentence), ("user", input_text)],
            temperature=0,
            response_format={"type": "text"},
        ).content

        self.history.append(("user", input_text))
        self.history.append(("assistant", sentence_to_say))
        return {"transition": transition, "sentence": sentence_to_say}

    def transition(self, action, input_text=None):
        if action == "stop":
            self.state = "stop"
            return
        if action == "none":
            return
        if action in self.transitions_graph[self.state]:
            if action in self.function_call:
                self.knowledge.update(self.function_call[action](input_text))
            self.state = self.transitions_graph[self.state][action]
        else:
            raise ValueError(
                f"No transition for action '{action}' in state '{self.state}'"
            )

    def get_state(self):
        return self.state
