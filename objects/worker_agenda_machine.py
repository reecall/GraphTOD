from .state_machine import StateMachine


class WorkerAgendaMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to the construction worker agenda ! How can I help you ? I'm here for you to find a tradesman for your project."

        transitions_graph = {
            "InitialState": {
                "new_project_quote": "RequestDetailsForTradesman",  # building trade à p-e garder
                "existing_project_quote": "RequestQuoteNumber",
                "existing_project_invoice": "RequestInvoiceNumber",
            },
            "RequestDetailsForTradesman": {
                "provide_info_for_quote_tradesman": "EvaluateQuotePossibilityWithTradesman",
            },
            "EvaluateQuotePossibilityWithTradesman": {
                "wait_for_quote": "ValidateQuoteTradesman",
                "ask_for_detailed_reason": "ExplainReason",
            },
            "ExplainReason": {
                "end": "Stop",
            },
            "ValidateQuoteTradesman": {
                "end": "Stop",
            },
            "RequestQuoteNumber": {
                "provide_info": "DecideIfExistingQuote",
            },
            "DecideIfExistingQuote": {
                "add_to_quote": "EvaluateQuotePossibilityWithTradesman",
            },
            "RequestInvoiceNumber": {
                "provide_info": "TellIfInvoiceExists",
            },
            "TellIfInvoiceExists": {
                "give_problem_detail": "Answer_problem",
            },
            "Answer_problem": {
                "send_message_to_tradesman": "SendingMessageTradesman",
            },
            "SendingMessageTradesman": {
                "end": "Stop",
            },
            "Stop": {},
        }

        function_call = {
            "add_to_quote": "/worker/add",
            "provide_info_for_quote_tradesman": "/worker/yesno",
            "provide_info": "/worker/yesno",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
