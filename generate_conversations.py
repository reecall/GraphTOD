import argparse
import json
import random as rd
from collections import UserDict

from datetime import datetime
from tqdm import tqdm
from faker import Faker
from objects import (
    RecipeMachine,
    DoctorMachine,
    RentCarMachine,
    HotelMachine,
    WorkerAgendaMachine,
)
from objects.AI_model import get_ai_model
from objects.user_machine import UserMachine
from dotenv import load_dotenv

load_dotenv(override=True)


def generate_convs(
    initial_machine,
    loop: int,
    do_save: bool = False,
    use_debug: bool = False,
    persona: bool = True,
):
    fake = Faker(locale="en_US")
    # check if machine is a class

    graph_description = (
        get_ai_model()()
        .invoke(
            f"I will send you a state-transition graph, and I want you to explain in one sentence the goal of this graph. The graph is the one of a phone agent. \n Here is the graph :\n {initial_machine.transitions_graph}",
            temperature=0.3,
        )
        .content
    )
    if use_debug:
        print(f"Graph description: {graph_description}")

    all_generated_conversations = []
    for _ in tqdm(range(loop), desc="Generating conversations ...", total=loop):
        # Copy the reference state machine
        sm = initial_machine.__class__(DEBUG=use_debug)
        if persona:
            # Generate with an LLM between 2 and 6 person caracteristics
            preferences = (
                get_ai_model()()
                .invoke(
                    f"Generate 10 general preferences for a person, where the conversation goal is : {graph_description}. Generate something in a json format such as {{'preferences': ['like fish', 'is tired', 'like astronomie']}}. Be creative.",
                    temperature=0.9,
                    response_format={"type": "json_object"},
                )
                .content
            )
            preferences = json.loads(preferences)["preferences"]
            # pick 4 random preferences
            preferences = rd.sample(preferences, 3)

            gender = rd.choice(["male", "female"])
            name = (
                fake.first_name_female()
                if gender == "female"
                else fake.first_name_male()
            )

            user = UserMachine(
                name=name,
                age=fake.random_int(min=18, max=80),
                gender=gender,
                informations=preferences,
            )
        else:
            user = UserMachine()
        seed = rd.randint(0, 999999999999)  # random seed
        user.set_state_machine(sm)
        try:
            conv, rd_walk = user.generate_conversation(
                get_ai_model(), graph_description, seed
            )
            # Convert to a dict
            if persona:
                conversation_data = {
                    "user": user.to_json(),
                    "conversation": conv,
                    "random_walk": rd_walk,
                    "seed": seed,
                    "time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                }
            else:
                conversation_data = {
                    "conversation": conv,
                    "random_walk": rd_walk,
                    "seed": seed,
                    "time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                }
            all_generated_conversations.append(conversation_data)
            if do_save:
                # save conversation in a file
                with open(
                    f"generated_conv/{initial_machine.__class__.__name__}_simulated_conversation_last_version.jsonl",
                    "a",
                ) as f:
                    f.write(
                        json.dumps(
                            conversation_data,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
        except Exception as e:
            print(f"ValueError: {e}")

    return all_generated_conversations


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--debug", action="store_true")
    args.add_argument("-n", "--num", type=int, default=1)
    args.add_argument("-m", "--machine", type=str)
    args.add_argument("-p", "--persona", action="store_true")
    args = args.parse_args()
    machines = {
        "recipe": RecipeMachine,
        "car": RentCarMachine,
        "doctor": DoctorMachine,
        "hotel": HotelMachine,
        "worker": WorkerAgendaMachine,
    }
    if args.machine not in machines:
        raise ValueError(f"Machine {args.machine} not found")
    generate_convs(
        initial_machine=machines[args.machine](DEBUG=args.debug),
        loop=args.num,
        do_save=True,
        use_debug=args.debug,
        persona=args.persona,
    )
