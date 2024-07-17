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
                "search_recipe": "shown_results",
                "pick_random_recipe": "shown_results",
            },
            "shown_results": {
                "explain_a_dish": "shown_results",
                "repeat_dishes_options": "shown_results",
                "select_a_recipe": "recipe_selected",
                "more_recipe_results": "shown_results",
            },
            "recipe_selected": {
                "begin_recipe": "started_task",
                "get_ingredients_and_quantities": "show_ingredients_and_quantities",
            },
            "show_ingredients_and_quantities": {"begin_recipe": "started_task"},
            "started_task": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "set_timer": "show_step",
                "done": "no_more_steps",
            },
            "show_step": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "set_timer": "show_step",
                "done": "no_more_steps",
            },
            "in-task_response": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "set_timer": "show_step",
                "done": "no_more_steps",
            },
            "no_more_steps": {"acknowledge": "stop"},
        }

        function_call = {
            "search_recipe": self.search_recipe,
            "pick_random_recipe": self.suggest_recipe,
            "select_a_recipe": self.select_i,
            "set_timer": self.set_timer,
            "more_results": self.more_results,
        }
        super().__init__(
            transitions_graph=transitions_graph,
            initial_state=initial_state,
            function_call=function_call,
            initial_sentence=initial_sentence,
            DEBUG=DEBUG,
        )

    def search_recipe(self, input_text: str, n_items: int = 3):
        model = reellm.get_llm(reellm.ModelName.MIXTRAL_8X22B)
        # Extract the recipe name from the user input
        if not self.knowledge.get("found_recipes"):
            recipe_name = model.invoke(
                [
                    (
                        "system",
                        "Your role is to extract only the food name from the input sentence of the user.\nReturn only the extracted plate of food type that you find in the input and nothing else.",
                    ),
                    ("user", input_text),
                ],
                temperature=0,
                max_tokens=6,
            ).content
            self.knowledge["searched_recipe"] = recipe_name
            if self.DEBUG:
                print(f"Recipe extracted: {recipe_name}")
        else:
            recipe_name = self.knowledge.get("searched_recipe")

        client = chromadb.PersistentClient()
        recipe_collection = client.get_collection("recipe")
        result = recipe_collection.query(
            self.embedder.embed_query(recipe_name), n_results=n_items
        )
        if self.DEBUG:
            # print finded recipes
            print(result["documents"][0])
        return {"found_recipes": result["documents"][0]}

    def suggest_recipe(self, _: str, n_items: int = 3):
        recipes = pd.read_json("data/corpus_recipe.jsonl", lines=True)
        # pick n_items random recipes
        result = recipes.sample(n_items)
        # keep only title
        result = result["title"].to_list()
        if self.DEBUG:
            # print finded recipes
            print(result)
        return {"found_recipes": result}

    def more_results(self, input_text: str):
        # find two more recipes to show
        if self.knowledge.get("searched_recipe"):
            new_recipes = self.search_recipe(
                self.knowledge.get("searched_recipe"),
                n_items=len(self.knowledge["found_recipes"]) + 2,
            )["found_recipes"]
        else:
            new_recipes = self.suggest_recipe(None, n_items=2)["found_recipes"]
        found_recipes = self.knowledge["found_recipes"]
        return {"found_recipes": found_recipes + new_recipes}

    def select_i(self, input_text):
        model = reellm.get_llm(reellm.ModelName.GPT_4_O)
        selection_generation = model.invoke(
            [
                (
                    "user",
                    (
                        f"Your role is to find the most probable index among the list {self.knowledge['found_recipes']} based on the user input and conversation history. "
                        f"Here is the history of the conversation:\n{self.history_to_string()}\n"
                        f"Your output must be a single number between 0 and {len(self.knowledge['found_recipes'])-1}, and nothing else."
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
            selected_recipe = self.knowledge["found_recipes"][selection_id]
        except IndexError:
            print(self.history_to_string())
            raise ValueError(
                f"{self.history_to_string()}\n\nInvalid selection index. Expected a number between 0 and {len(self.knowledge['found_recipes'])-1}, got {selection_id}.\nLLM generation : {selection_generation}"
            )
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

    def set_timer(self, input_text):
        model = reellm.get_llm(reellm.ModelName.MIXTRAL_8X7B)
        time = model.invoke(
            f"Extract the time from the sentence: {input_text}. Give only the extracted time and nothing else. If no time is found, return '0'.",
            temperature=0,
            max_tokens=15,
        ).content
        if self.DEBUG:
            print(f"Time extracted: {time}")
        return None


if __name__ == "__main__":
    print(RecipeMachine.get_random_walk(seed=42))
