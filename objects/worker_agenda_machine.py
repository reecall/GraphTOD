from .state_machine import StateMachine


class WorkerAgendaMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to the construction worker agenda ! How can I help you ? I'm here for you to find a tradesman for your project."
        #For example build a house, repair your toilet leak, install new windows, etc. Do you want to start a new quote, or do you have an existing quote or invoice ?"
        #me rajoute des fausses transitions pour avec "start_a_new_quote" par ex,

        transitions_graph = {
            "InitialState": {
                "request": "RequestTypeWork",
            },
            "RequestTypeWork": {
                "new_quote_building_trade": "RequestDetailsForTradesman",
                "existing_quote_building_trade": "RequestQuoteNumber",
                "existing_invoice_building_trade": "RequestInvoiceNumber",
            },
            "RequestDetailsForTradesman": {
                "provide_info_for_quote_tradesman": "EvaluateQuotePossibilityWithTradesman",
            },
            "EvaluateQuotePossibilityWithTradesman": {
                "wait_for_quote_un": "ValidateQuoteTradesman",
                "wait_for_quote_deux": "OtherRequest",
            },
            "OtherRequest": {
                "other_request": "RequestTypeWork",
                "end": "Stop",
            },
            "ValidateQuoteTradesman": {
                "other_request": "RequestTypeWork",
                "end": "Stop",
            },
            "RequestQuoteNumber": {
                "provide_info": "DecideIfExistingQuote",
            },
            "DecideIfExistingQuote": {
                "add_to_quote": "EvaluateQuotePossibilityWithTradesman",
            },
            "RequestInvoiceNumber": {
                "provide_info": "SearchAPIInvoices",
            },
            "SearchAPIInvoices": {
                "give_problem_detail": "Answer_problem",
            },
            "Answer_problem": {
                "send_message_to_tradesman": "SendingMessageTradesman",
                "other_request": "RequestTypeWork",
            },
            "SendingMessageTradesman": {
                "end": "Stop",
            },
            "Stop": {},
        }

        #TODO : adapt function call
        function_call = {
            "add_to_quote": "/worker/add",
            "EvaluateQuotePossibilityWithTradesman": "/worker/yesno",
            "SearchAPIInvoices" : "/worker/yesno",
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
