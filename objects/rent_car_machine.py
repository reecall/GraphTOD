from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_state = "start"
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        transitions_graph = {
            "start": {
                "to_rent_car": "search_car_options",
                "ask_for_help": "provide_help",
            },
            "provide_help": {
                "answer_question": "ask_rental_details",
                "transfer_to_agent": "stop",
            },
            "search_car_options": {
                "show_car_options": "shown_car_options",
                "no_cars_available": "stop",
            },
            "shown_car_options": {
                "explain_a_car": "shown_car_options",
                "select_a_car": "confirm_rental_details",
                "more_car_options": "search_car_options",
            },
            "confirm_rental_details": {
                "confirm_details": "process_payment",
                "modify_details": "ask_rental_details",
            },
            "process_payment": {
                "payment_successful": "confirm_reservation",
                "payment_failed": "ask_payment_details",
            },
            "ask_payment_details": {
                "provide_payment_details": "process_payment",
                "cancel_rental": "stop",
            },
            "confirm_reservation": {
                "ask_a_question": "provide_help",
                "no_more_help": "stop",
            },
        }

        function_call = {
            "select_a_car": self.select_i,
            "show_car_options": "http://127.0.0.1:8000/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_state=initial_state,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
