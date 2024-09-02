from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"


        transitions_graph_maya = {
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
                "select_date": "ValidateReservation",
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

        function_call_maya = {
            "select_vehicle": self.select_i,
            "select_date": self.select_i,
            "see_vehicles": "/car/search",
            "provide_date": "/car/date",
        }

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
        }

        function_call = {
            "select_vehicule": self.select_i,
            "see_vehicules": "/car/search",
        }

        super().__init__(
            transitions_graph=transitions_graph_maya,
            initial_sentence=initial_sentence,
            function_call=function_call_maya,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
