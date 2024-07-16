import argparse
import json
from datetime import datetime

from tqdm import tqdm
from reellm import get_llm, ModelName
from objects.recipe_machine import RecipeMachine
from dotenv import load_dotenv

load_dotenv(override=True)
choosen_recipes = []


def generate_conv(model, DEBUG=False):
    history = []
    sm = RecipeMachine(DEBUG=DEBUG)
    system = (
        "system",
        (
            "Act like a human on who's speaking to a cooking agent. "
            "Your goal is to cook a recipe with the help of the agent. "
            "Follow the agent's instructions, or propositions, and if you don't know what to say, you can ask for help."
            "You should be creative in your answer to the agent, and be creative about the recipe you want to cook (choose simple recipes). "
            f" Don't choose a recipe mentioned in: {choosen_recipes}.\n"
            "Your answer need to be short and concise, look like oral language, as someone speeking to siri or google home. "
            "Feel free to ask a question about the recipe at any time, if you need informations to make the recipe (cooking details, ingredient quantity, etc...). "
            "The answer must be formatted as an instruction or a question to the agent, and nothing else. "
            "Follow the conversation flow and try to reach the end of the conversation. "
        ),
    )
    while True:
        if DEBUG:
            print(f"Agent: {sm.history[-1][1]}")
        history.append(
            {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
        )
        if DEBUG:
            print(f"Current state: {sm.state}")
        history_copy = sm.history.copy()
        # swith roles (assistant -> user and user -> assistant)
        history_copy = [
            ("assistant" if role == "user" else "user", text)
            for role, text in sm.history
        ]
        user_input = model.invoke([system] + history_copy, temperature=0.8).content
        if len(history) == 1:
            choosen_recipes.append(user_input)
        if DEBUG:
            print(f"You: {user_input}")
        output = sm.get_response(user_input)
        history.append(
            {"role": "user", "text": user_input, "transition": output["transition"]}
        )
        if sm.state == "stop":
            if DEBUG:
                print(f"Agent: {sm.history[-1][1]}")
            history.append(
                {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
            )
            break
    return history


def main(loop: int, DEBUG: bool = False):
    model = get_llm(ModelName.GPT_4_O)
    for _ in tqdm(range(loop), desc="Generating conversations ...", total=loop):
        try:
            conv = generate_conv(model, DEBUG=DEBUG)
            # save conversation in a file
            with open("simulated_conversation.jsonl", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "conversation": conv,
                            "time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--debug", action="store_true")
    args.add_argument("-n", "--num", type=int, default=1)
    args = args.parse_args()
    main(loop=args.num, DEBUG=args.debug)
