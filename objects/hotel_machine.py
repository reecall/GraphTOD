from .state_machine import StateMachine


class HotelMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, what can I do for you ?"  # do you need help find a hotel or deal with a previous booking ?"

        transitions_graph = {
            "InitialState": {
                "search_hotels": "DisplayHotels",
                "cancel_or_modify_reservation": "BookingFound",
            },
            "DisplayHotels": {
                "ask_for_more_hotels": "DisplayHotels",
                "select_hotel": "AskPaymentInfo",
                "ask_for_details": "DisplayHotelDetails",
            },
            "DisplayHotelDetails": {
                "select_hotel": "AskPaymentInfo",
                "ask_for_more_hotel": "DisplayHotels",
            },
            "AskPaymentInfo": {
                "check_payment_type": "AskPaymentConfirmation",
            },
            "AskPaymentConfirmation": {
                "process_payment": "PaymentAccepted",
            },
            "PaymentAccepted": {
                "request_invoice": "SendInvoice",
                "end": "Stop",
            },
            "SendInvoice": {
                "end": "Stop",
            },
            "BookingFound": {
                "criteria_to_modify": "ModificationPossible",  # TODO : possible or not to modify
                "refund": "CheckRefund",
            },
            "ModificationPossible": {
                "add_criteria": "OtherCriteriaAdded",
            },
            "OtherCriteriaAdded": {
                "end": "Stop",
            },
            "CheckRefund": {
                "wait_refund_one": "RefundDone",  # TODO : yes / no for the refund
                "wait_refund_two": "RefundImpossible",
            },
            "RefundDone": {
                "end": "Stop",
            },
            "RefundImpossible": {
                "ask_for_compensation": "SuggestCompensation",
                "end": "Stop",
            },
            "SuggestCompensation": {
                "user_accepts": "CompensationAccepted",
                "user_refuses": "CompensationRefused",
            },
            "CompensationAccepted": {
                "end": "Stop",
            },
            "CompensationRefused": {
                "end": "Stop",
            },
        }

        function_call = {
            "select_hotel": self.select_i,
            "search_hotels": "/hotel/search",
            "ask_for_more_hotels": "/hotel/search",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
