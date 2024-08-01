from .state_machine import StateMachine


class RecipeMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_state = "start"
        initial_sentence = "Hello ! What do you want to cook today ?"
        transitions_graph = {
            "start": {
                "search_recipe": "shownResults",
                "pick_random_recipe": "shownResults",
            },
            "shownResults": {
                "explain_a_dish": "shownResults",
                "repeat_recipes_options": "shownResults",
                "select_a_recipe": "presentRecipeDetails",
                "more_recipe_results": "shownResults",
            },
            "presentRecipeDetails": {
                "start_cooking": "startedTask",
                "get_ingredients_of_recipe": "showIngredientsAndQuantities",
            },
            "showIngredientsAndQuantities": {
                "start_cooking": "started_task",
            },
            "startedTask": {
                "question_about_recipe": "recipeQuestionResponse",
                "continue_recipe": "showStep",
            },
            "showStep": {
                "question_about_recipe": "recipeQuestionResponse",
                "continue_recipe": "showStep",
                "end_recipe": "stop",
            },
            "recipeQuestionResponse": {
                "question_about_recipe": "recipeQuestionResponse",
                "continue_recipe": "showStep",
                "end_recipe": "stop",
            },
        }

        function_call = {
            "search_recipe": "http://127.0.0.1:8000/recipe/search",
            "pick_random_recipe": "http://127.0.0.1:8000/recipe/suggest",
            "select_a_recipe": self.select_i,
            "more_results": "http://127.0.0.1:8000/recipe/more_results",
        }
        super().__init__(
            transitions_graph=transitions_graph,
            initial_state=initial_state,
            function_call=function_call,
            initial_sentence=initial_sentence,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )


if __name__ == "__main__":
    print(RecipeMachine.get_random_walk(seed=42))
