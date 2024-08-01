import json
import re
import pandas as pd
import random as rd
import requests

from reellm import get_llm, get_embedding, ModelName


class StateMachine:
    def __init__(
        self,
        transitions_graph: dict,
        initial_state: str,
        function_call: dict,
        datafile: str,
        initial_sentence: str = "Hello ! What can I do for you ?",
        DEBUG: bool = False,
    ):
        self.state = initial_state
        self.transitions_graph = transitions_graph
        self.history = [("assistant", initial_sentence)]
        self.path = []
        self.function_call = function_call
        self.knowledge = {}
        self.embedder = get_embedding(ModelName.EMBEDDING_LARGE)
        self.llm = get_llm(ModelName.GPT_4_O)
        self.DEBUG = DEBUG
        self.datafile = datafile
        if self.DEBUG:
            print(f"Debug mode is enabled for {self.__class__.__name__}")

    def __str__(self):
        return f"StateMachine(state={self.state})"

    def to_json(self):
        return {
            "state": self.state,
            "transitions_graph": self.transitions_graph,
        }

    def history_to_string(self):
        return "\n".join([f"{role}: {sentence}" for role, sentence in self.history])

    def get_next_transitions(self):
        return list(self.transitions_graph[self.state].keys())

    def get_response(self, input_text: str):
        # understand what's the transition ; then apply the transition ; then return the response
        transition_prompt = (
            "You're a agent specialized in state transition graph. "
            "You should act as an agent, based on the user input, the current state and the transitions graph. "
            "You should return the transition that suit the best following the user input as a json. "
            "Use elements from your context knowledge for your answer when you think it's relevant. "
            "Here is the information about the history of the conversation:\n"
            f"{self.history_to_string()}\n"
            "Here is all the transitions you can take, based on the current state :\n"
            f"{"\n-".join(self.get_next_transitions())}\n"
            "Pick one transition listed above following the context of the user input, or return the transition 'none' if you think there is no transition corresponding. "
            "If you think that's the end of the conversation, return the transition 'stop'. "
            "Here is what you know in your context knowledge:\n"
            f"{self.knowledge}\n"
            "Predict just the transition, and nothing else, as : {'transition': 'transition_name'}"
        )
        transition = self.llm.invoke(
            [("system", transition_prompt), ("user", f"Here is the user input : '{input_text}'")],
            temperature=0,
            response_format={"type": "json_object"},
        ).content.lower()
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
                "The sentence should be short and look like oral language. "
                "Your generation must look like a human transcription, and not like a machine generated text. "
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
                "Your generation must look like a human transcription, and not like a machine generated text. "
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
                "You should return the next sentence to say to the user. "
                "The sentence should be short and look like oral language. "
                "Be concise and go straight to the point. "
                "Your generation must look like a human speech transcription, and not like a machine generated text. "
                "Insert elements in your context knowledge for your answer when you think it's relevant. "
                "Here is what you know in your context :\n"
                f"{self.knowledge}"
                f"Your sentence must correspond to the state '{self.state}'\n"
                "Here is the information about the history of the conversation:\n"
                f"{self.history_to_string()}\n"
                "You need to inspire you from the state name to generate the next sentence, and use all the knowledge you can. Generate just a response, and nothing else."
                "Do not forget to be polite and helpful."
            )

        sentence_to_say = self.llm.invoke(
            [
                ("system", next_sentence),
                (
                    "user",
                    f"Here is the user input: {input_text}. Generate a response to this.",
                ),
            ],
            temperature=0,
            response_format={"type": "text"},
        ).content
        self.history.append(("user", input_text))
        self.history.append(("assistant", sentence_to_say))
        return {"transition": transition, "sentence": sentence_to_say}

    def transition(
        self, action: str, input_text: str = None, enable_function_call: bool = True
    ):
        self.path.append((self.state, action))
        if action == "stop":
            self.state = "stop"
            return
        if action == "none":
            return
        if action in self.transitions_graph[self.state]:
            if action in self.function_call and enable_function_call:
                f_result = self.function_calling(action, input_text)
                if f_result:
                    self.knowledge.update(f_result)
            self.state = self.transitions_graph[self.state][action]
        else:
            raise ValueError(
                f"No transition for action '{action}' in state '{self.state}'"
            )

    def function_calling(self, action: str, input_text: str = None):
        if callable(self.function_call[action]):
            return self.function_call[action](input_text)
        else:
            # It is an endpoint
            response = requests.post(
                self.function_call[action],
                json={"input_text": input_text, "knowledge": self.knowledge},
            )
            return response.json()

    def select_i(self, input_text: str):
        list_of_findings = self.knowledge["search_result"]
        selection_generation = self.llm.invoke(
            [
                (
                    "user",
                    (
                        f"Your role is to find the most probable index among the list {list_of_findings} based on the user input and conversation history. "
                        f"Here is the history of the conversation:\n{self.history_to_string()}\n"
                        f"Your output must be a single number between 0 and {len(list_of_findings)-1}, and nothing else."
                        f"\nUser input was : {input_text}"
                    ),
                ),
            ],
            temperature=0,
        ).content
        if self.DEBUG:
            print(f"LLM output: {selection_generation}")
        # sub re in the generation
        try:
            selection_id = int(re.sub(r"[^0-9]", "", selection_generation)[-1])
        except Exception:
            print(self.history_to_string())
            raise ValueError(
                f"{self.history_to_string()}\n\nInvalid selection format. Expected a number inside, got '{selection_generation}'.\nInput text was : {input_text}"
            )
        try:
            selected_recipe = list_of_findings[selection_id]
        except IndexError:
            print(self.history_to_string())
            raise ValueError(
                f"{self.history_to_string()}\n\nInvalid selection index. Expected a number between 0 and {len(list_of_findings)-1}, got {selection_id}.\nLLM generation : {selection_generation}"
            )
        if self.DEBUG:
            print(f"Selected element: {selected_recipe}")
        # open recipes
        recipes = pd.read_json(self.datafile, lines=True)
        # Get the recipe where title = selected_recipe
        recipe_json = recipes[recipes["title"] == selected_recipe].to_json(
            orient="records"
        )
        # convert to json
        return {"selected_element": recipe_json}

    def get_state(self):
        return self.state

    @classmethod
    def get_random_walk(cls, seed=None):
        """
        Get a random walk from the state-transition graph, formatted as a list of tuples (state, action).
        """
        sm = cls()
        walk = []
        rd.seed(seed)
        while sm.state != "stop":
            action = rd.choice(list(sm.transitions_graph[sm.state].keys()))
            walk.append((sm.state, action))
            sm.transition(action, enable_function_call=False)
        return walk
