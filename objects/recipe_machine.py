from .state_machine import StateMachine


class RecipeMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello ! What do you want to cook today ?"
        transitions_graph = {
            "InitialState": {
                "ask_to_search_recipe": "ShowRecipiesResults",
                "pick_random_recipe": "ShowRecipiesResults",
            },
            "ShowRecipiesResults": {
                "ask_details_on_a_dish": "ShowRecipiesResults",
                "ask_to_repeat_results": "ShowRecipiesResults",
                "select_a_recipe": "PresentRecipeDetails",
                "ask_more_recipe_results": "ShowRecipiesResults",
            },
            "PresentRecipeDetails": {
                "start_cooking": "StartedTask",
                "get_ingredients_of_recipe": "ShowIngredientsAndQuantities",
            },
            "ShowIngredientsAndQuantities": {
                "start_cooking": "StartedTask",
            },
            "StartedTask": {
                "ask_question_about_recipe": "RecipeQuestionResponse",
                "ask_next_step": "ShowStep",
            },
            "ShowStep": {
                "ask_question_about_recipe": "RecipeQuestionResponse",
                "ask_next_step": "ShowStep",
                "end": "Stop",
            },
            "RecipeQuestionResponse": {
                "ask_question_about_recipe": "RecipeQuestionResponse",
                "ask_next_step": "ShowStep",
                "end": "Stop",
            },
        }

        function_call = {
            "ask_to_search_recipe": "/recipe/search",
            "pick_random_recipe": "/recipe/suggest",
            "select_a_recipe": self.select_i,
            "ask_more_recipe_results": "/recipe/more_results",
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
