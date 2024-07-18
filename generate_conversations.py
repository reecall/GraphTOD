import argparse
import json
import random as rd

from datetime import datetime
from tqdm import tqdm
from reellm import get_llm, ModelName
from state_machines.recipe_machine import RecipeMachine, StateMachine
from dotenv import load_dotenv

load_dotenv(override=True)
choosen_recipes = []


def get_prompt(rd_walk, machine: StateMachine, step):
    global choosen_recipes, DEBUG
    next_transition = rd_walk[step][1] if step < len(rd_walk) else "stop"
    detailed_intent = (
        get_llm(ModelName.GPT_3_5_TURBO)
        .invoke(
            [
                ("system", "You are an agent expert in state-transition graphs"),
                (
                    "user",
                    f"Explain in few words the user intent that hides behind this transition name : {next_transition}",
                ),
            ],
        )
        .content
    )
    if DEBUG:
        print(f"    Next wanted transition is {next_transition}")
        print(f"    Detailed intent: {detailed_intent}")
    return [
        (
            "system",
            (
                "Your goal is to generate the next user sentence of a dialog between a human and a cooking agent, based on the intent of the user. "
                "To generate the next user input, you must follow the conversation flow and what the agent is asking you to do. "
                "For context, here is the history of the conversation, where you are the user:\n"
                f"{machine.history_to_string()}\n"
                "Your generation need to be short, concise, look like a line of dialog, as someone speeking to a home assistant. "
                "Your generation must look like a human transcription, and not like a machine generated text. "
                "If the agent ask you to choose among multiple choices, you should choose one of them, and tell the agent your choice.\n"
                f"You should be creative in your answer to the agent, and be creative about the recipe you want to cook (choose simple recipes). Don't choose a recipe mentioned in: {choosen_recipes}.\n"
                if step == 0
                else ""
                "Return just the next sentence to say to the agent, and nothing else."
            ),
        ),
        (
            "user",
            f'Here is the intent of the user : {detailed_intent}.\n Based on this, what should the user answer to "{machine.history[-1][1]}"?',
        ),
    ]


def generate_conv(model, seed: int):
    global choosen_recipes, DEBUG
    history = []
    sm = RecipeMachine(DEBUG=DEBUG)
    rd_walk = RecipeMachine.get_random_walk(seed=seed)
    if DEBUG:
        print("Random walk:")
        print(rd_walk)
    step = 0
    while True:
        if DEBUG:
            print(f"Agent: {sm.history[-1][1]}")
        history.append(
            {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
        )
        if DEBUG:
            print(f"Current state: {sm.state}")

        # get system prompt
        prompt = get_prompt(rd_walk=rd_walk, machine=sm, step=step)

        user_input = model.invoke(
            prompt,
            temperature=0.3,
        ).content

        if len(history) == 1:
            chose_recipe = user_input

        if DEBUG:
            print(f"You: {user_input}")
        output = sm.get_response(user_input)
        history.append(
            {"role": "user", "text": user_input, "transition": output["transition"]}
        )
        step += 1
        if sm.state == "stop":
            if DEBUG:
                print(f"Agent: {sm.history[-1][1]}")
            history.append(
                {"role": "assistant", "text": sm.history[-1][1], "state": sm.state}
            )
            break
    choosen_recipes.append(chose_recipe)
    return history, rd_walk


def main(loop: int):
    global DEBUG
    model = get_llm(ModelName.GPT_4_O)
    for _ in tqdm(range(loop), desc="Generating conversations ...", total=loop):
        seed = rd.randint(0, 999999999999)  # random seed
        try:
            conv, rd_walk = generate_conv(model, seed)
            # save conversation in a file
            with open("simulated_conversation.jsonl", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "conversation": conv,
                            "random_walk": rd_walk,
                            "seed": seed,
                            "time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except ValueError as e:
            print(f"ValueError: {e}")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--debug", action="store_true")
    args.add_argument("-n", "--num", type=int, default=1)
    args = args.parse_args()

    DEBUG = args.debug
    main(loop=args.num)
