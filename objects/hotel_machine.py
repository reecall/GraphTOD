from .state_machine import StateMachine


class HotelMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, what can I do for you ?"  # do you need help find a hotel or deal with a previous booking ?"

        transitions_graph = {
            "InitialState": {
                "search_hotels": "DisplayHotels",
                "ask_cancelling_or_modifying_reservation": "BookingFound",
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
                "criteria_to_modify": "ModificationPossible",
                "refund": "AnswerForRefund",
            },
            "ModificationPossible": {
                "add_criteria": "OtherCriteriaAdded",
            },
            "OtherCriteriaAdded": {
                "end": "Stop",
            },
            "AnswerForRefund": {
                "contest_refund_decision": "DetailsRefundDecision",
                "accept_decision": "Stop",
            },
            "DetailsRefundDecision": {
                "ask_for_another_compensation": "AlternativeCompensation",
                "accept_decision": "Stop",
            },
            "AlternativeCompensation": {
                "user_accepts": "CompensationAccepted",
                "user_refuses": "CompensationRefused",
            },
            "CompensationAccepted": {
                "end": "Stop",
            },
            "CompensationRefused": {
                "negociate_compensation": "AlternativeCompensation",
                "end": "Stop",
            },
            "Stop": {},
        }

        function_call = {
            "select_hotel": self.select_i,
            "search_hotels": "/hotel/search",
            "ask_for_more_hotels": "/hotel/search",
            # "refund" : "/hotel/refund", #TODO add in API
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
