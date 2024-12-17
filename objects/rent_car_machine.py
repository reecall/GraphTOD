from .state_machine import StateMachine


class RentCarMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to Rent A Car ! How can I help you ?"

        transitions_graph = {
            "InitialState": {
                "ask_question": "ResponseFAQ",
                "has_a_reservation": "AskLicensePlateNumber",
                "make_a_reservation": "AskDateAndTime",
            },
            "ResponseFAQ": {
                "end": "Stop",
                "other_request": "InitialState",
            },
            "AskLicensePlateNumber": {
                "check_license_plate_number": "AskPickupCancelExtend",
            },
            "AskPickupCancelExtend": {
                "pick_up_vehicle": "ShowPickUpInfos",
                "cancel_reservation": "CancellationSuccess",
                "extend_reservation": "AskExtendDuration",
            },
            "AskExtendDuration": {
                "check_extend_possibility": "ValidateReservation",
            },
            "ShowPickUpInfos": {
                "end": "Stop",
            },
            "CancellationSuccess": {
                "end": "Stop",
                "make_a_reservation": "AskDateAndTime",
            },
            "AskDateAndTime": {
                "check_dates_availability": "ShowAvailableDates",
            },
            "ShowAvailableDates": {
                "select_date": "ValidateReservation",
                "see_vehicles": "ShowAvailableVehicles",
            },
            "ShowAvailableVehicles": {
                "check_dates_availability": "ShowAvailableDates",
                "select_vehicle": "ValidateReservation",
                "ask_more_info": "MoreInfo",
            },
            "ValidateReservation": {
                "end": "Stop",
            },
            "MoreInfo": {
                "return_vehicle_disponibilities": "ShowAvailableDates",
            },
            "Stop": {},
        }

        function_call = {
            "select_vehicle": self.select_i,
            "select_date": self.select_i,
            "see_vehicles": "/car/search",
            "check_dates_availability": "/car/date",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
