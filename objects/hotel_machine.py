from .state_machine import StateMachine


class HotelMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, what can I do for you ? do you need help find a hotel or deal with a previous booking ?"

        transitions_graph = {
            "InitialState": {
                "request": "RequestType",
            },
            "InScopeResponse": {
                "end": "stop",
                "other_request": "RequestType",
            },
            "RequestType": {
                "search_hotel": "DisplayHotels",
                "cancel_or_modify_reservation": "BookingFound",
            },
            "DisplayHotels": {
                "display_more": "DisplayHotelDetails",
                "select_hotel": "BookHotel",
            },
            "DisplayHotelDetails": {
                "show_other_hotels": "DisplayHotels",
            },
            "BookHotel": {
                "choose_payment_type": "Payment",
            },
            "Payment": {
                "request_invoice": "SendInvoice",
                "end": "Stop",
                "other_request": "RequestType",
            },
            "SendInvoice": {
                "end": "Stop",
                "other_request": "RequestType",
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
                "other_request": "RequestType",
            },
            "CheckRefund": {
                "wait_refund_un": "Refund",
                "wait_refun_deux": "RefundImpossible",
            },
            "Refund": {
                "other_request": "RequestType",
                "end": "Stop",
            },
            "RefundImpossible": {
                "end": "Stop",
                "other_request": "RequestType",
            }
        }


        #TODO : adapt function call
        function_call = {
            "select_hotel": self.select_i,
            "search_hotel": "/hotel/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )