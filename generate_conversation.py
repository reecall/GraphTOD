import json

from reellm import ModelName, get_llm
from objects.recipe_machine import RecipeMachine
from dotenv import load_dotenv

load_dotenv(override=True)

model = get_llm(ModelName.GPT_4_O)
sm = RecipeMachine()
conversation = []
conversation.append(
    (
        "system",
        (
            "You're a agent specialized in state transition graph."
            "You should act as an agent, based on the user input, the current state and the transitions graph. "
            "You should return the transition, the next state and the response of the agent, as a json."
        ),
    )
)

conversation.append(
    (
        "user",
        (
            "I want you to generate a dataset of conversations based one the structure of a state transition graph. "
            "You should also generate the response of the user and the agent. "
            "Try to generate a dataset of 50 possible conversation that is likely to happend, and with various scenarios. "
            "Return the dataset as a json. "
            "Here is the information about the state transition graph:\n"
            f"{sm.to_json()}"
        ),
    )
)

output = model.invoke(
    conversation, temperature=0.1, response_format={"type": "json_object"}
).content

# dumb json in output_conv.json
output = json.loads(output)
with open("output_conv.json", "w") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)
