from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        transitions_graph = {
            "Start": {
                "to_rent_car": "SearchCarOptions",
                "ask_for_help": "ProvideHelp",
            },
            "ProvideHelp": {
                "answer_question": "ask_rental_details",
                "transfer_to_agent": "stop",
            },
            "SearchCarOptions": {
                "show_car_options": "ShownCarOptions",
                "no_cars_available": "stop",
            },
            "ShownCarOptions": {
                "explain_a_car": "ShownCarOptions",
                "select_a_car": "ConfirmRentalDetails",
                "more_car_options": "search_car_options",
            },
            "ConfirmRentalDetails": {
                "confirm_details": "ProcessPayment",
                "modify_details": "ask_rental_details",
            },
            "ProcessPayment": {
                "payment_successful": "ConfirmReservation",
                "payment_failed": "AskPaymentDetails",
            },
            "AskPaymentDetails": {
                "provide_payment_details": "process_payment",
                "cancel_rental": "stop",
            },
            "ConfirmReservation": {
                "ask_a_question": "ProvideHelp",
                "no_more_help": "stop",
            },
        }

        function_call = {
            "select_a_car": self.select_i,
            "show_car_options": "http://127.0.0.1:8000/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
