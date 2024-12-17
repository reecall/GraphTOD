# SynTOD - Reecall

Implementation of the [SynTOD](https://arxiv.org/abs/2404.14772v1) paper, which is a model for task-oriented dialogue dataset generation.

Demo at : https://graphtod.reecall.com/

## Introduction

This framework allows the construction of state-transition graphs to model user-agent interactions in dialogue systems or other event-based applications. It uses explicit nodes and transitions to define actions and reactions in the system, facilitating integration with APIs and custom functions.\
Additionally, this framework enables the generation of dialogue datasets for training natural language models.

The dialogues are generated by following the steps of the conversation. These steps are defined through a random walk on the state-transition graph.
It is generated at each step of the conversation.
Among the transitions accessible from the current node, one is chosen randomly.
The LLM, acting either as the agent or the user, will generate a sentence using the selected transition.

## Environment variables

To use the program with command lines, you need to set the environment variables. You can do this by creating a `.env` file in the root directory of the project and adding the following variables:

```plaintext
DEFAULT_OPENAI_TYPE =
DEFAULT_OPENAI_DEPLOYMENT_NAME=
DEFAULT_OPENAI_ENDPOINT=
DEFAULT_OPENAI_API_KEY=
```

For `DEFAULT_OPENAI_TYPE`, you can choose between 'openai' and 'azure_openai'. Also, `DEFAULT_OPENAI_ENDPOINT` is needed only for 'azure_openai' type.

## Graph Formalism

### Graph Definition

The state-transition graph is a data structure that defines the possible actions of the user and the corresponding responses of the agent. It consists of nodes and transitions that describe the interactions between the user and the agent. In the code, the graph is defined as a dictionary of nodes and transitions.

### Node Structure

A node is defined by a name followed by its possible transitions. Each transition is described by a user action and the corresponding agent action, leading to another node. Nodes should be named in CamelCase and transitions in snake_case. By default, the initial node is named "InitialState."
A node is an action of the agent, using an action verb and a complement that describes how to apply the verb.

The name of a node is written as follows:
"VerbComplement".

#### Example

"CollectLicensePlateNumber", "ValidateReservation", "AskAppointmentDate", ...

```plaintext
"Node" : { transitions }
```

### Defining a Transition

A transition is the user's action. Transitions from one node to another are defined by a pair `user_action: AgentAction`, where `AgentAction` is the name of the next node.
To name the transition, the complement works as it does for nodes.

The name of a transition is written as follows:
"verb_complement"

#### Example

"cancel_reservation", "select_doctor", "schedule_appointment", ...

```plaintext
"user_action" : "AgentAction"
```

### Building a Graph

A graph is built as a Python dictionary.
It consists of nodes and transitions that will be written following the definitions above.

```python
myDict = {
    "Node1": {
        "edge": "Node2"
        }
}

myDict = {
    "VerbComplement1": {
        "verb_complement": "VerbComplement2",
        "verb_complement": "VerbComplement1",
    },
    "VerbComplement2": {
    ...
    }
}
```

### Naming Conventions for Nodes and Transitions

-   Nodes and transitions must be named using action verbs such as "ask," "schedule," "search," "show," etc.
-   Naming should be explicit to clearly indicate the action performed in the prompt.

#### Example of Action Verbs:

Ask,
Schedule,
Edit,
Identify,
Reschedule,
Cancel,
Remind,
Search,
Select,
Check,
Show,
Pick-up,
Extend,
Book,
Extend,
Make,
Provide,
Return,
Collect,
Validate,
Explain,
Send,
Give,
Confirm

### Using Functions in Transitions

Transitions can trigger functions whose results will be used in the prompt of the next node. These functions can contain API calls to retrieve the information necessary for the action.
This is how additional capabilities can be added to the agent.

#### Example of a Function

```python
def select_i(api_url, parameters):
    # Implementation here
```

The function `select_i` is used to have the LLM select from a list of items.

#### Example of Function Use in an Agent

Here, we call an API for the action _see_vehicles_ and use the function _select_i_ for the action _select_vehicle_.

```python
graph = {
            "AskVehicleType": {
                "see_vehicles": "VehiclesAvailables",
            },
            "VehiclesAvailables": {
                "select_vehicle": "AskNameToValidateReservation",
            }
}
function_call = {
    "select_vehicle": select_i,
    "see_vehicles": "/car/search",
}
```

### Minimum Requirements

To use this framework, the following elements are necessary:

1. **Starting Sentence**: The initial sentence to start the interaction.
2. **Initial Node**: The node from which the interaction begins.
3. **Graph of Possible Actions**: The definition of transitions between nodes.
4. **APIs Associated with Transitions**: The APIs to call during transitions.

### Example of a State-Transition Graph

Here is an example of defining a state-transition graph:

```json
{
	"Start": {
		"ask_question": "Faq",
		"schedule_appointment": "AskPatientInfo",
		"edit_appointment": "AskPatientName"
	},
	"AskPatientInfo": {
		"search_doctor_list": "ShowDoctorList"
	}
}
```

### Persona

The framework automatically generates user personas based on the content of the agent, created by a language model (LLM).
The agent's content is summarized by an LLM and then used as context to generate user personalities that are relevant to the agent.

Each persona has an automatically generated name, age, and their preferences.

Example:
For a medical appointment booking agent, the generated personas will have preferences for doctors, schedules, etc.

### Additional Explanations

### Explications supplémentaires

#### A écrire au propre
Les transitions générées par le random walk ne seront pas suivies quand on oublie une transition 
qui permet de passer logiquement à la suite ou bien quand on lui demande un truc illogique. 
Respecter la logique des choses : un état fait une seule chose, on ne suppose pas qu'une action 
supplémentaire sera réalisée dedans. Par exemple : avoir une date de rdv c'est uniquement 
donner les dates des rdv, ça ne comprend pas l'interaction avec l'utilisateur (sa réponse sera 
une transition vers un autre noeud). On décomposera en demande d'une date de rdv, réponse avec 
les dates de rdv, puis sélection des dates de rdv. 

bien respecter ACTION humain, puis ACTION machine
on ne peux pas enchaîner deux actions d'affilée pour la machine comme pour l'humain

respecter la logique : les transitions déclenchées par l'humain ne peuvent pas nécessiter une action de la 
machine pour fonctionner correctement, sinon ça veut dire qu'il manque un noeud ou une transition pour gérer 
ces cas là.

Pour être sur que le résumé du graphe soit correct pour la persona, il faut que les informations 
critiques pour les actions de l'agent soient dans les premiers noeuds du graphes. Explication possible :
les LLMs sont plus sensibles aux informations au début du contexte.

Trick : pour faire faire un choix je fais une transition "wait_for_choice_un" : ChoiceValidated, 
puis "wait_for_choice_deux" : ChoiceNotValidated, pour que au hasard il choisisse l'un ou l'autre
et utilise les bons noeuds pour le choix correspondant.

Expliquer comment faire des étapes pour laisser le temps à l'agent de répondre sans que l'utilisateur
le coupe en lui demandant quelque chose de nouveau derrière.
=======
The transitions generated by the random walk will not be followed when a transition that logically leads to the next step is missing or when an illogical request is made.
Respect the logic of things: a state does one thing only, and we don't assume that an additional action will be performed within it. For example: having an appointment date only means giving the appointment dates, it does not include interaction with the user (their response will be a transition to another node). We will break it down into requesting an appointment date, responding with the appointment dates, and then selecting the appointment dates.

### Full Example of an Agent Graph

This graph defines an agent that manages vehicle reservations.

It can use a function to select from a list and two APIs to know the available reservation dates and to see the available vehicles.

```json
        {
            "InitialState": {
                "ask_question": "ResponseFAQ",
                "pick_up_vehicle": "AskLicensePlateNumber",
                "cancel_reservation": "AskLicensePlateNumber",
                "extend_reservation": "AskLicensePlateNumber",
                "make_a_reservation": "AskDateAndTime",
            },
            "ResponseFAQ": {
                "end": "stop",
                "other_request": "InitialState",
            },
            "AskLicensePlateNumber": {
                "give_license_plate": "CollectLicensePlateNumber",
            },
            "CollectLicensePlateNumber": {
                "pick_up_vehicle": "InfoViaAPI",
                "cancel_reservation": "Cancellation",
                "extend_reservation": "AskDateAndTime",
            },
            "InfoViaAPI": {
                "end": "stop",
            },
            "Cancellation": {
                "end": "stop",
                "make_a_reservation": "AskDateAndTime",
            },
            "AskDateAndTime": {
                "provide_date": "ResponseAccordingToAPIDispo",
            },
            "ResponseAccordingToAPIDispo": {
                "select_date": "ValidateReservation",
                "see_vehicles": "VehiclesAvailableAccordingToAPIDispo",
            },
            "VehiclesAvailableAccordingToAPIDispo": {
                "provide_date": "ResponseAccordingToAPIDispo",
                "select_vehicle": "ValidateReservation",
                "ask_more_info": "MoreInfo",
            },
            "ValidateReservation": {
                "end": "stop",
            },
            "MoreInfo": {
                "return_vehicle_disponibilities": "VehiclesAvailableAccordingToAPIDispo",
            },
            "stop": {}
        }

        function_call = {
            "select_vehicle": self.select_i,
            "select_date": self.select_i,
            "see_vehicles": "http://127.0.0.1:8000/car/search",
            "provide_date": "http://127.0.0.1:8000/car/date",
        }
```
