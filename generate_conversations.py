import argparse
import json
import random as rd

from datetime import datetime
from tqdm import tqdm
from faker import Faker
from reellm import get_llm, ModelName
from objects.recipe_machine import RecipeMachine
from objects.user_machine import UserMachine
from dotenv import load_dotenv

load_dotenv(override=True)


def main(loop: int):
    global DEBUG
    fake = Faker(locale="fr_FR")
    model = get_llm(ModelName.GPT_4_O)
    for _ in tqdm(range(loop), desc="Generating conversations ...", total=loop):
        # Generate with an LLM between 2 and 6 person caracteristics
        preferences = (
            get_llm(ModelName.GPT_4_O)
            .invoke(
                "Generate 2 to 6 general preferences for a person, in a json format such as {'preferences': ['like fish', 'is tired']}. Be creative.",
                temperature=1,
                response_format={"type": "json_object"},
            )
            .content
        )
        print(preferences)
        preferences = json.loads(preferences)["preferences"]

        gender = rd.choice(["male", "female"])
        name = (
            fake.first_name_female() if gender == "female" else fake.first_name_male()
        )
        user = UserMachine(
            name=name,
            age=fake.random_int(min=18, max=80),
            gender=gender,
            informations=preferences,
        )
        seed = rd.randint(0, 999999999999)  # random seed
        sm = RecipeMachine(DEBUG=DEBUG)
        user.set_state_machine(sm)
        try:
            conv, rd_walk = user.generate_conversation(model, seed)
            # save conversation in a file
            with open("simulated_conversation.jsonl", "a") as f:
                f.write(
                    json.dumps(
                        {
                            "user": user.to_json(),
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
