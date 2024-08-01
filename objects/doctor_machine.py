from .state_machine import StateMachine


class DoctorMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_state = "start"
        initial_sentence = "Hello, welcome to your doctor office ! How can I help you ?"
        transitions_graph = {
            "start": {
                "ask_question": "faq",
                "schedule_appointment": "patientInfo",
                "edit_appointment": "askPatientName",
            },
            "faq": {
                "end": "stop",
                "other_request": "start",
            },
            "askDoctorName": {
                "identify_appointment_API": "idAppointmentAPI",
                "reschedule_appointment": "datesAPI",
            },
            "askPatientName": {
                "identify_appointment": "confirmAppointmentFound",
            },
            "confirmAppointmentFound": {
                "cancel_appointment": "appointmentCancellation",
                "reminder_appointment": "appointmentReminder",
                "reschedule_appointment": "datesAPI",
            },
            "appointmentCancellation": {
                "end": "stop",
                "other_request": "start",
            },
            "appointmentReminder": {
                "end": "stop",
                "other_request": "start",
            },
            "patientInfo": {
                "view_doctor_list": "doctorList",
            },
            "doctorList": {
                "available_dates_api": "datesAPI",
            },
            "datesAPI": {
                "show_more": "moreInfo",
                "choose_date": "appointmentBooked",
                "other_doctor": "doctorList",
            },
            "moreInfo": {"return_dates_api": "datesAPI"},
            "appointmentBooked": {
                "end": "stop",
                "other_request": "start",
            },
            "stop": {},
        }

        function_call = {}

        super().__init__(
            transitions_graph=transitions_graph,
            initial_state=initial_state,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_recipe.jsonl",
            DEBUG=DEBUG,
        )
