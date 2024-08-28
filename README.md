# SynTOD - Reecall

Implementation of the [SynTOD](https://arxiv.org/abs/2404.14772v1) paper, which is a model for task-oriented dialogue dataset generation.

## Introduction

Ce framework permet de construire des graphes d'état-transition pour modéliser les interactions utilisateur-agent dans des systèmes de dialogue ou d'autres applications basées sur des événements. Il utilise des nœuds et des transitions explicites pour définir les actions et les réactions dans le système, en facilitant l'intégration avec des API et des fonctions personnalisées. \
De plus, ce framework permet de générer des dataset de dialogue pour l'entraînement de modèles de langage naturel.

Les dialogues sont générés en suivant les étapes de la conversation. Ces étapes sont définie grâce un random walk sur le graphe d'état-transition.
Il généré à chaque étape de la conversation.
Parmi les transitions accessibles à partir du noeud courant on en choisi une aléatoirement.
Le LLM qui joue soit l'agent, soit l'utilisateur devra générer une phrase en utilisant la transition sélectionnée.

## Formalisme des graphes

### Definition d'un graphe

Le graphe d'état-transition est une structure de données qui définit les actions possibles de l'utilisateur et les réponses correspondantes de l'agent. Il est composé de nœuds et de transitions qui décrivent les interactions entre l'utilisateur et l'agent. Dans le code, le graphe est défini comme un dictionnaire de nœuds et de transitions.

### Structure d'un Nœud

Un nœud est défini par un nom suivi de ses transitions possibles. Chaque transition est décrite par une action utilisateur et l'action correspondante de l'agent, qui mène à un autre nœud. Les nœuds doivent être nommés en CamelCase et les transitions en snake_case. Par défaut, le nœud initial est nommé "InitialState".
Un noeud est une action de l'agent, il utilise un verbe d'action et un complément qui décrit comment appliquer le verbe.

Le nom d'un noeud est écrit tel que : 
"VerbeComplément".


#### Exemple

"CollectLicensePlateNumber", "ValidateReservation", "AskAppointmentDate", ...

```plaintext
"Noeud" : { transitions }
```

### Définir une Transition

Une transition est l'action de l'utilisateur. Les transitions d'un nœud à l'autre sont définies par un couple `action_utilisateur : ActionAgent`, où `ActionAgent` est le nom du nœud suivant.
Pour nommer la transition le complément fonctionne comme pour les noeuds.

Le nom d'une transition est écrit tel que :
"verbe_complément"


#### Exemple

"cancel_reservation" , "select_doctor", "schedule_appointment", ...

```plaintext
"action_utilisateur" : "ActionAgent"
```

### Construire un graphe 

Un graphe est construit comme un dictionnaire python.
Il est composé de nœuds et de transitions qui seront écrit en suivant les définitions ci-dessus.
```
monDict = { 
    "Noeud1" :  { 
        "arête" : "Noeud2" 
        }
}

monDict =  { 
    "VerbeComplément1" : { 
        "verbe_complément" : "VerbeComplément2",
        "verbe_complément" : "VerbeComplément1",
    },
    "VerbeComplément2" : {
    ...
    }
}
```

### Précisions sur le nommage des Nœuds et des Transitions

-   Les nœuds et les transitions doivent être nommés par des verbes d'action tels que "ask", "schedule", "search", "show", etc.
-   Le nommage doit être explicite pour indiquer clairement l'action réalisée dans le prompt.

#### Exemple de verbes d'action :

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

### Utilisation des Fonctions dans les Transitions

Les transitions peuvent déclencher des fonctions dont le résultat sera utilisé dans le prompt du nœud suivant. Ces fonctions peuvent contenir des appels API pour récupérer les informations nécessaires à l'action.
C'est avec ça qu'on peut rajouter des capacités supplémentaires à l'agent.

#### Exemple de Fonction

```plaintext
def select_i(api_url, parameters):
    # Implementation here
```

La fonction select_i sert à faire sélectionner au LLM parmis une liste d'éléments.

#### Exemple d'utilisation de Fonction dans un agent

Ici on appelle une api pour l'action *see_vehicules* et on utilise la fonction *select_i* pour l'action *select_vehicule*.

```python
graphe = {
            "AskVehiculeType": {
                "see_vehicules": "VehiculesAvailables",
            },
            "VehiculesAvailables": {
                "select_vehicule": "AskNameToValidateReservation",
            }
}
function_call = {
    "select_vehicule": select_i,
    "see_vehicules": "/car/search", 
}
```

### Exigences Minimales

Pour utiliser ce framework, les éléments suivants sont nécessaires :

1. **Phrase de départ** : La phrase initiale pour démarrer l'interaction.
2. **Nœud initial** : Le nœud à partir duquel commence l'interaction.
3. **Graphe des actions possibles** : La définition des transitions entre les nœuds.
4. **APIs associées aux transitions** : Les APIs à appeler lors des transitions.

### Exemple de Graphe d'État-Transition

Voici un exemple de définition d'un graphe d'état-transition :

```python
TransitionsGraph = {
    "Start": {
        "ask_question": "Faq",
        "schedule_appointment": "AskPatientInfo",
        "edit_appointment": "AskPatientName",
    },
    "AskPatientInfo": {
        "search_doctor_list": "ShowDoctorList",
    }
}
```

### Persona

Le framework génère automatiquement des personas d'utilisateurs en fonction du contenu de l'agent, créés par un modèle de langage (LLM). 
Le contenu de l'agent est résumé par un LLM puis utilisé en tant que contenxte pour générer des personnalités d'utilisateurs 
qui sont pertinentes avec l'agent.

Chaque persona a un nom généré automatiquement, un âge, et leurs préférences.

Exemple :
Agent de prise de rdv médicaux, les persona générés auront des préférences pour les médecins, les horaires, etc.



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



### Exemple entier de graphe d'agent

Ce graphe définit un agent qui gére des réservations de véhicules.

Il peut utiliser une fonction pour sélectionner dans une liste et deux API pour connaître les dates disponibles de réservation
et pour voir les véhicules disponibles.

```python
        transitions_graph = {
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

### LLM utilisé
GPT 4o


