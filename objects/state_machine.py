import json
import re
import pandas as pd
import random as rd
import requests

from objects.AI_model import AIModel, get_ai_model


class StateMachine:
    def __init__(
        self,
        transitions_graph: dict,
        function_call: dict,
        datafile: str = None,
        initial_state: str = "InitialState",
        initial_sentence: str = "Hello ! What can I do for you ?",
        api_adress = "http://127.0.0.1:8000",
        DEBUG: bool = False,
    ):
        # Define string name of prefab functions
        self.prefab_functions = {
            "select_i": self.select_i,
        }
        self.state = initial_state
        self.transitions_graph = transitions_graph
        self.history = [("assistant", initial_sentence)]
        self.initial_sentence = initial_sentence
        self.path = []

        self.function_call = function_call
        # convert string to function
        for key, value in self.function_call.items():
            if value in self.prefab_functions.keys():
                self.function_call[key] = self.prefab_functions[value]

        self.api_adress = api_adress
        self.knowledge = {}
        self.llm: AIModel = get_ai_model()
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
    
    def get_config(self) -> dict:
        return {
            "transitions_graph": self.transitions_graph,
            "function_call": self.function_call,
            "datafile": self.datafile,
            "initial_sentence": self.history[0][1],
            "api_adress": self.api_adress,
        }

    def history_to_string(self):
        return "\n".join([f"{role}: {sentence}" for role, sentence in self.history])

    def get_next_transitions(self):
        return list(self.transitions_graph[self.state].keys())
    
    def detect_intent(self, input_text: str):
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
            "If you think that's the end of the conversation, return the transition 'end'. "
            "Here is what you know in your context knowledge:\n"
            f"{self.knowledge}\n"
            "Predict just the transition, and nothing else, as : {'transition': 'transition_name'}"
        )
        transition = self.llm().invoke(
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
        if transition not in self.transitions_graph[self.state]:    
            raise ValueError(
                f"Invalid transition. Expected a transition in {self.transitions_graph[self.state]}, got {transition}"
                + "\n"
                + self.history_to_string()
            )
        return transition

    def get_response(self, input_text: str):
        # understand what's the transition ; then apply the transition ; then return the response
        transition = self.detect_intent(input_text)
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
        elif transition == "end":
            next_sentence = (
                "You're a agent specialized in state transition graph. "
                "You should act as an agent, based on the user input, the current state and the transitions graph. "
                "You should return the next sentence to say to the user, knowing that it's the end of the conversation, and that there will be no user entry after this sentence. "
                "The sentence should be short and look like oral language. "
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

        sentence_to_say = self.llm().invoke(
            [
                ("system", next_sentence),
                (
                    "user",
                    f"Here is the user input: {input_text}. Generate a response to this.",
                ),
            ],
            temperature=0.3,
            response_format={"type": "text"},
        ).content
        self.history.append(("user", input_text))
        self.history.append(("assistant", sentence_to_say))
        return {"transition": transition, "sentence": sentence_to_say}

    def transition(
        self, action: str, input_text: str = None, enable_function_call: bool = True
    ):
        self.path.append((self.state, action))
        if action == "end":
            self.state = "Stop"
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
                self.api_adress + self.function_call[action],
                json={"input_text": input_text, "knowledge": self.knowledge},
            )
            return response.json()

    def select_i(self, input_text: str):
        try:
            list_of_findings = self.knowledge["search_result"]
        except KeyError:
            print(self.knowledge)
            raise ValueError(
                f"No search result in the context knowledge.\nInput text was : {input_text}"
            )
        selection_generation = self.llm().invoke(
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
            selected_element = list_of_findings[selection_id]
        except IndexError:
            print(self.history_to_string())
            raise ValueError(
                f"{self.history_to_string()}\n\nInvalid selection index. Expected a number between 0 and {len(list_of_findings)-1}, got {selection_id}.\nLLM generation : {selection_generation}"
            )
        if self.DEBUG:
            print(f"Selected element: {selected_element}")
        if not self.datafile:
            return {"selected_element": selected_element}
        # open datafile
        recipes = pd.read_json(self.datafile, lines=True)
        # Get the data where title = selected_element
        recipe_json = recipes[recipes["title"] == selected_element].to_json(
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
        while sm.state.lower() != "stop":
            action = rd.choice(list(sm.transitions_graph[sm.state].keys()))
            walk.append((sm.state, action))
            sm.transition(action, enable_function_call=False)
        return walk
