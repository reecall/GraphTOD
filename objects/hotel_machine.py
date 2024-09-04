from .state_machine import StateMachine


class HotelMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, what can I do for you ?" # do you need help find a hotel or deal with a previous booking ?"

        transitions_graph = {
            "InitialState": {
                "request": "RequestType",
            },
            "InScopeResponse": {
                "end": "Stop",
                "other_booking": "RequestType",
            },
            "RequestType": {
                "search_hotel": "DisplayHotels",
                "cancel_or_modify_reservation": "BookingFound",
            },
            "DisplayHotels": {
                "ask_for_more_hotel": "DisplayHotels",
                "select_hotel": "BookHotel",
                "ask_for_details": "DisplayHotelDetails",
            },
            "DisplayHotelDetails": {
                "select_hotel": "BookHotel",
                "ask_for_more_hotel": "DisplayHotels",
            },
            "BookHotel": {
                "ask_payment_type": "PaymentProcess",
            },
            "PaymentProcess": {
                "pay": "PaymentAccepted",
            },
            "PaymentAccepted": {
                "request_invoice": "SendInvoice",
                "end": "Stop",
                "other_request": "InScopeResponse",
                "other_booking": "RequestType",
            },
            "SendInvoice": {
                "end": "Stop",
                "other_request": "InScopeResponse",
                "other_booking": "RequestType",
            },
            "BookingFound": {
                "criteria_to_modify": "ModificationPossible",
                "refund": "CheckRefund",
            },
            "ModificationPossible": {
                "add_criteria": "OtherCriteriaAdded",
            },
            "OtherCriteriaAdded": {
                "end": "Stop",
                "other_request": "InScopeResponse",
                "other_booking": "RequestType",
            },
            "CheckRefund": {
                "wait_refund_un": "Refund",
                "wait_refund_deux": "RefundImpossible",
            },
            "Refund": {
                "other_request": "InScopeResponse",
                "other_booking": "RequestType",
                "end": "Stop",
            },
            "RefundImpossible": {
                "end": "Stop",
                "other_request": "InScopeResponse",
                "other_booking": "RequestType",
            },
            "Stop": {},
        }


        #TODO : adapt function call
        function_call = {
            "select_hotel": self.select_i,
            "search_hotel": "/hotel/search",
            "ask_for_more_hotel": "/hotel/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )