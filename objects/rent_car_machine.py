from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"
        transitions_graph = {
            "InitialState": {
                "make_a_reservation": "AskLicensePlateNumber",
                "edit_a_reservation": "AskDateAndTime",
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
                "end": "Stop",
            },
            "Cancellation": {
                "end": "Stop",
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
                "end": "Stop",
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
