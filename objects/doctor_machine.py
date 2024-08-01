from .state_machine import StateMachine


class DoctorMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to your doctor office ! How can I help you ?"
        transitions_graph = {
            "Start": {
                "ask_question": "Faq",
                "schedule_appointment": "AskPatientInfo",
                "edit_appointment": "AskPatientName",
            },
            "Faq": {
                "end": "stop",
                "other_request": "Start",
            },
            "AskDoctorName": {
                "identify_appointment_API": "idAppointmentAPI",
                "reschedule_appointment": "ShowAvailableDates",
            },
            "AskPatientName": {
                "identify_appointment": "ConfirmAppointmentFound",
            },
            "ConfirmAppointmentFound": {
                "cancel_appointment": "AppointmentCancellation",
                "reminder_appointment": "AppointmentReminder",
                "reschedule_appointment": "ShowAvailableDates",
            },
            "AppointmentCancellation": {
                "end": "stop",
                "other_request": "Start",
            },
            "AppointmentReminder": {
                "end": "stop",
                "other_request": "Start",
            },
            "AskPatientInfo": {
                "search_doctor_list": "ShowDoctorList",
            },
            "ShowDoctorList": {
                "select_doctor": "AskAppointmentDate",
            },
            "AskAppointmentDate": {
                "check_available_dates": "ShowAvailableDates",
            },
            "ShowAvailableDates": {
                "show_more_dates": "MoreInfo",
                "select_dates": "appointmentBooked",
                "other_doctor": "ShowDoctorList",
            },
            "MoreInfo": {
                "search_available_date": "ShowAvailableDates",
            },
            "AppointmentBooked": {
                "end": "Stop",
                "other_request": "Start",
            },
            "Stop": {},
        }

        function_call = {}

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_doctor.jsonl",
            DEBUG=DEBUG,
        )

        self.knowledge["available_dates"] = [
            "8th october",
            "12th october",
            "15th october",
            "17th october",
            "20th october",
        ]
