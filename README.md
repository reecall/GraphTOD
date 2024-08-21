# SynTOD - Reecall

Implementation of the [SyntTOD](https://arxiv.org/abs/2404.14772v1) paper, which is a model for task-oriented dialogue dataset generation.

## Introduction

Ce framework permet de construire des graphes d'état-transition pour modéliser les interactions utilisateur-agent dans des systèmes de dialogue ou d'autres applications basées sur des événements. Il utilise des nœuds et des transitions explicites pour définir les actions et les réactions dans le système, en facilitant l'intégration avec des API et des fonctions personnalisées. /
De plus, ce framework permet de générer des dataset de dialogue pour l'entraînement de modèles de langage naturel.

## Formalisme des graphes

### Definition d'un graph

Le graphe d'état-transition est une structure de données qui définit les actions possibles de l'utilisateur et les réponses correspondantes de l'agent. Il est composé de nœuds et de transitions qui décrivent les interactions entre l'utilisateur et l'agent. Dans le code, le graphe est défini comme un dictionnaire de nœuds et de transitions.

### Structure d'un Nœud

Un nœud est défini par un nom suivi de ses transitions possibles. Chaque transition est décrite par une action utilisateur et l'action correspondante de l'agent, qui mène à un autre nœud. Les nœuds doivent être nommés en CamelCase et les transitions en snake_case. Par défaut, le nœud initial est nommé "InitialState".

#### Exemple

```plaintext
Nom : { transitions }
```

### Définir une Transition

Les transitions d'un nœud à l'autre sont définies par un couple `action_utilisateur : ActionAgent`, où `ActionAgent` est le nom du nœud suivant.

#### Exemple

```plaintext
action_utilisateur : ActionAgent
```

### Nommer les Nœuds et les Transitions

-   Les nœuds et les transitions doivent être nommés par des verbes d'action tels que "ask", "schedule", "search", "show", etc.
-   Le nommage doit être explicite pour indiquer clairement l'action réalisée dans le prompt.

### Utilisation des Fonctions dans les Transitions

Les transitions peuvent déclencher des fonctions dont le résultat sera utilisé dans le prompt du nœud suivant. Ces fonctions peuvent contenir des appels API pour récupérer les informations nécessaires à l'action.

#### Exemple de Fonction

```plaintext
def select_i(api_url, parameters):
    # Implementation here
```

### Exigences Minimales

Pour utiliser ce framework, les éléments suivants sont nécessaires :

1. **Phrase de départ** : La phrase initiale pour démarrer l'interaction.
2. **Nœud initial** : Le nœud à partir duquel commence l'interaction.
3. **Graphe des actions possibles** : La définition des transitions entre les nœuds.
4. **APIs associées aux transitions** : Les APIs à appeler lors des transitions.

### Exemple de Graph d'État-Transition

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
