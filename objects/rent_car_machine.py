from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        transitions_graph = {
            "InitialState": {
                "ask_question": "ResponseFAQ",
                "pick_up_vehicle": "AskLicensePlateNumber",
                "cancel_reservation": "AskLicensePlateNumber",
                "extend_reservation": "AskLicensePlateNumber",
                "make_a_reservation": "AskDateAndTime",
            },
            "ResponseFAQ": {
                "end": "stop",
                "other_request": "InitialState",
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
            "Stop": {},
        }

        function_call = {
            "select_vehicle": self.select_i,
            "see_vehicles": "/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
