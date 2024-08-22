from .state_machine import StateMachine


class DoctorMachine(StateMachine):
    def __init__(self, DEBUG=False):
        initial_sentence = "Hello, welcome to your doctor office ! How can I help you ?"
        transitions_graph = {
            "InitialState": {
                "schedule_doctor_appointment": "AskPatientInfo",
                "edit_doctor_appointment": "AskPatientName",
            },
            "AskPatientName": {
                "identify_appointment": "ConfirmAppointmentFound",
            },
            "ConfirmAppointmentFound": {
                "cancel_appointment": "AppointmentCancellation",
                "reminder_appointment": "AppointmentReminder",
                "reschedule_appointment": "ShowAvailableSlots",
            },
            "AppointmentCancellation": {
                "end": "Stop",
            },
            "AppointmentReminder": {
                "end": "Stop",
            },
            "AskPatientInfo": {
                "save_patient_info": "AskDoctorName",
            },
            "AskDoctorName": {
                "search_doctor_in_list": "ShowDoctorList",
            },
            "ShowDoctorList": {
                "select_doctor": "ShowAvailableSlots",
            },
            "ShowAvailableSlots": {
                "select_dates": "AppointmentBooked",
                "other_doctor": "ShowDoctorList",
            },
            "AppointmentBooked": {
                "end": "Stop",
            },
        }

        function_call = {
            "search_doctor_in_list": "/doctor/search",
            "select_doctor": self.select_i,
        }

        super().__init__(
            transitions_graph=transitions_graph,
            initial_sentence=initial_sentence,
            function_call=function_call,
            datafile="data/corpus_doctor.jsonl",
            DEBUG=DEBUG,
        )
