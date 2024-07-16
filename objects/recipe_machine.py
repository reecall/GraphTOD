import chromadb
import pandas as pd
from .state_machine import StateMachine
import re
import reellm


class RecipeMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_state = "start"
        initial_sentence = "Hello ! What do you want to cook today ?"
        transitions_graph = {
            "start": {
                "search_recipe": "show_all_founded_recipes",
            },
            "show_all_founded_recipes": {
                "select_i": "describe_selected_recipe",
            },
            "no_results": {
                "stop": "stop",
            },
            "describe_selected_recipe": {
                "begin_acknowledge": "started_task",
            },
            "started_task": {
                "in-task qa": "in-task_response",
                "acknowledge": "show_step",
                "next_step": "show_step",
                "goto_step": "show_step",
                "done": "show_step",
            },
            "show_step": {
                "done": "no_more_step",
                "goto_step": "show_step",
                "next_step": "show_step",
                "acknowledge": "show_step",
                "in-task qa": "in-task_response",
            },
            "in-task_response": {
                "in-task qa": "in-task_response",
                "done": "show_step",
                "goto_step": "show_step",
                "next_step": "show_step",
                "acknowledge": "show_step",
            },
            "no_more_step": {
                "acknowledge": "stop",
            },
        }
        function_call = {
            "search_recipe": self.search_recipe,
            "select_i": self.select_i,
        }
        super().__init__(
            transitions_graph=transitions_graph,
            initial_state=initial_state,
            function_call=function_call,
            initial_sentence=initial_sentence,
            DEBUG=DEBUG,
        )

    def search_recipe(self, input_text):
        model = reellm.get_llm(reellm.ModelName.MIXTRAL_8X7B)
        # Extract the recipe name from the user input
        recipe_name = model.invoke(
            f"Extract the recipe name from the sentence: {input_text}. Give only the extracted recipe and nothing else.",
            temperature=0,
            max_tokens=6,
        ).content
        if self.DEBUG:
            print(f"Recipe extracted: {recipe_name}")
        client = chromadb.PersistentClient()
        recipe_collection = client.get_collection("recipe")
        result = recipe_collection.query(
            self.embedder.embed_query(recipe_name), n_results=3
        )
        if self.DEBUG:
            # print the choosen recipes
            print(result["documents"])
        return {"founded_recipes": result["documents"][0]}

    def select_i(self, input_text):
        model = reellm.get_llm(reellm.ModelName.COMMAND_R)
        selection_id = model.invoke(
            f"Select the index of the most probable recipe in {self.knowledge['founded_recipes']} base on the anwer {input_text} to {self.history[-1][1]}. Return only the index number of the good recipe, between 0 and {len(self.knowledge['founded_recipes'])-1}, and nothing else.",
            temperature=0,
            max_tokens=1,
        ).content
        if self.DEBUG:
            print(f"LLM output: {selection_id}")
        # sub re in the generation
        selection_id = int(re.sub(r"[^0-9]", "", selection_id))

        selected_recipe = self.knowledge["founded_recipes"][selection_id]
        if self.DEBUG:
            print(f"Selected recipe: {selected_recipe}")
        # open recipes
        recipes = pd.read_json("data/corpus_recipe.jsonl", lines=True)
        # Get the recipe where title = selected_recipe
        recipe_json = recipes[recipes["title"] == selected_recipe].to_json(
            orient="records"
        )
        # convert to json
        return {"recipe_selected": recipe_json}


if __name__ == "__main__":
    sm = RecipeMachine()
    try:
        sm.transition("search_recipe")
        print(sm.get_state())  # should print 'shown_results'

        sm.transition("select_i")
        print(sm.get_state())  # should print 'option_selected'

        sm.transition("begin")
        print(sm.get_state())  # should print 'started_task'

        sm.transition("next_step")
        print(sm.get_state())  # should print 'show_step'
    except ValueError as e:
        print(e)
