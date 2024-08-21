from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        transitions_graph = {
            "InitialState": {
                "ask_question": "ResponseFAQ",
                "manage_a_reservation": "AskLicensePlateNumber",
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
                "pick_up_vehicule": "PickUpInfo",
                "cancel_reservation": "Cancellation",
                "extend_reservation": "AskDateAndTime",
            },
            "PickUpInfo": {
                "other_request": "InitialState",
                "end": "stop",
            },
            "Cancellation": {
                "end": "stop",
                "make_a_reservation": "AskDateAndTime",
            },
            "AskDateAndTime": {
                "check_date_available": "AskVehiculeType",
            },
            "AskVehiculeType": {
                "see_vehicules": "VehiculesAvailables",
            },
            "VehiculesAvailables": {
                "select_vehicule": "AskNameToValidateReservation",
            },
            "AskNameToValidateReservation": {
                "process_reservation": "SummaryReservation",
            },
            "SummaryReservation": {
                "end": "stop",
                "other_request": "InitialState",
            },
            "Stop": {},
        }

        function_call = {
            "select_vehicule": self.select_i,
            "see_vehicules": "/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
