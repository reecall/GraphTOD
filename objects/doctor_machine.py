from .state_machine import StateMachine


class DoctorMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to your doctor office ! How can I help you ?"
        transitions_graph = {
            "InitialState": {
                "ask_question": "Faq",
                "schedule_appointment": "AskPatientInfo",
                "edit_appointment": "AskPatientName",
            },
            "Faq": {
                "end": "stop",
                "other_request": "InitialState",
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
                "other_request": "InitialState",
            },
            "AppointmentReminder": {
                "end": "stop",
                "other_request": "InitialState",
            },
            "AskPatientInfo": {
                "save_patient_info": "AskDoctorName",
            },
            "AskDoctorName": {
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
                "other_request": "InitialState",
            },
            "Stop": {},
        }

        function_call = {
            "search_doctor_list": "http://127.0.0.1:8000/doctor/search",
            "select_doctor": self.select_i,
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_doctor.jsonl",
            DEBUG=DEBUG,
        )
