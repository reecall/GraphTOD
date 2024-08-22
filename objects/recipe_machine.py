from .state_machine import StateMachine


class RecipeMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello ! What do you want to cook today ?"
        transitions_graph = {
            "InitialState": {
                "search_recipe": "ShownResults",
                "pick_random_recipe": "ShownResults",
            },
            "ShownResults": {
                "explain_a_dish": "ShownResults",
                "repeat_recipes_options": "ShownResults",
                "select_a_recipe": "PresentRecipeDetails",
                "more_recipe_results": "ShownResults",
            },
            "PresentRecipeDetails": {
                "start_cooking": "StartedTask",
                "get_ingredients_of_recipe": "ShowIngredientsAndQuantities",
            },
            "ShowIngredientsAndQuantities": {
                "start_cooking": "started_task",
            },
            "StartedTask": {
                "question_about_recipe": "RecipeQuestionResponse",
                "continue_recipe": "ShowStep",
            },
            "ShowStep": {
                "question_about_recipe": "RecipeQuestionResponse",
                "continue_recipe": "ShowStep",
                "end_recipe": "Stop",
            },
            "RecipeQuestionResponse": {
                "question_about_recipe": "RecipeQuestionResponse",
                "continue_recipe": "ShowStep",
                "end_recipe": "Stop",
            },
            "Stop": {},
        }

        function_call = {
            "search_recipe": "/recipe/search",
            "pick_random_recipe": "/recipe/suggest",
            "select_a_recipe": self.select_i,
            "more_results": "/recipe/more_results",
        }
        super().__init__(
            transitions_graph=transitions_graph,
            function_call=function_call,
            initial_sentence=initial_sentence,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )


if __name__ == "__main__":
    print(RecipeMachine.get_random_walk(seed=42))
