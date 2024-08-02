from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        # transitions_graph = {
        #     "start": {
        #         "rent_car": "search_car_options",
        #         "ask_for_help": "provide_help",
        #     },
        #     "provide_help": {
        #         "answer_question": "ask_rental_details",
        #         "transfer_to_agent": "stop",
        #     },
        #     "search_car_options": {
        #         "show_car_options": "shown_car_options",
        #         "no_cars_available": "stop",
        #     },
        #     "shown_car_options": {
        #         "explain_a_car": "shown_car_options",
        #         "select_a_car": "confirm_rental_details",
        #         "more_car_options": "search_car_options",
        #     },
        #     "confirm_rental_details": {
        #         "confirm_details": "process_payment",
        #         "modify_details": "ask_rental_details",
        #     },
        #     "process_payment": {
        #         "payment_successful": "confirm_reservation",
        #         "payment_failed": "ask_payment_details",
        #     },
        #     "ask_payment_details": {
        #         "provide_payment_details": "process_payment",
        #         "cancel_rental": "stop",
        #     },
        #     "confirm_reservation": {
        #         "ask_a_question": "provide_help",
        #         "no_more_help": "stop",
        #     },
        # }

        transitions_graph = {
            "start": {
                "ask_question": "ResponseFAQ",
                "pick_up_vehicle": "AskLicensePlateNumber",
                "cancel_reservation": "AskLicensePlateNumber",
                "extend_reservation": "AskLicensePlateNumber",
                "make_a_reservation": "AskDateAndTime",
            },
            "ResponseFAQ": {
                "end": "stop",
                "other_request": "start",
            },
            "AskLicensePlateNumber": {
                "give_license_plate": "CollectLicensePlateNumber",
            },
            "CollectLicensePlateNumber": {
                "pick_up_vehicle": "InfoViaAPI",
                "cancel_reservation": "Cancellation",
                "extend_reservation": "AskDateAndTime",
            },
            "InfoViaAPI": {
                "end": "stop",
            },
            "Cancellation": {
                "end": "stop",
                "make_a_reservation": "AskDateAndTime",
            },
            "AskDateAndTime": {
                "provide_date": "ResponseAccordingToAPIDispo",
            },
            "ResponseAccordingToAPIDispo": {
                "see_vehicles": "VehiclesAvailableAccordingToAPIDispo",
            },
            "VehiclesAvailableAccordingToAPIDispo": {
                "provide_date": "ResponseAccordingToAPIDispo",
                "select_vehicle": "ValidateReservation",
                "ask_more_info": "MoreInfo",
            },
            "ValidateReservation": {
                "end": "stop",
            },
            "MoreInfo": {
                "return_vehicle_disponibilities": "VehiclesAvailableAccordingToAPIDispo",
            },
            "stop": {}
        }

        function_call = {
            "select_vehicle": self.select_i,
            "see_vehicles": "http://127.0.0.1:8000/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
