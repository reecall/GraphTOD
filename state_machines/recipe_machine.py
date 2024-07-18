from .state_machine import StateMachine


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
                "select_a_recipe": "present_recipe_details",
                "more_recipe_results": "shown_results",
            },
            "present_recipe_details": {
                "begin_recipe": "started_task",
                "get_ingredients_and_quantities": "show_ingredients_and_quantities",
            },
            "show_ingredients_and_quantities": {"begin_recipe": "started_task"},
            "started_task": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "done": "no_more_steps",
            },
            "show_step": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "done": "no_more_steps",
            },
            "in-task_response": {
                "in-task_qa": "in-task_response",
                "next_step": "show_step",
                "goto_step": "show_step",
                "done": "no_more_steps",
            },
            "no_more_steps": {"acknowledge": "stop"},
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
            DEBUG=DEBUG,
        )


if __name__ == "__main__":
    print(RecipeMachine.get_random_walk(seed=42))
