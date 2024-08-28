import argparse
import json
import random as rd

from datetime import datetime
from tqdm import tqdm
from faker import Faker
from reellm import get_llm, ModelName
from objects import RecipeMachine, DoctorMachine, RentCarMachine, HotelMachine, WorkerAgendaMachine
from objects.user_machine import UserMachine
from dotenv import load_dotenv

load_dotenv(override=True)


def main(machine, loop: int):
    global DEBUG
    fake = Faker(locale="en_US")
    model = get_llm(ModelName.GPT_4_O)
    sm = machine(DEBUG=DEBUG)
    graph_description = (
        get_llm(ModelName.GPT_4_O)
        .invoke(
            f"I will send you a state-transition graph, and I want you to explain in one sentence the goal of this graph. The graph is the one of a phone agent. \n Here is the graph :\n {sm.transitions_graph}",
            # f"Here is also the opening sentence an agent would say with this graph ",
            temperature=0.3,
        )
        .content
    )
    if DEBUG:
        print(f"Graph description: {graph_description}")
    for _ in tqdm(range(loop), desc="Generating conversations ...", total=loop):
        sm = machine(DEBUG=DEBUG)
        # Generate with an LLM between 2 and 6 person caracteristics
        preferences = (
            get_llm(ModelName.GPT_4_O)
            .invoke(
                f"Generate 10 general preferences for a person, where the conversation goal is : {graph_description}. Generate something in a json format such as {{'preferences': ['like fish', 'is tired', 'like astronomie']}}. Be creative.",
                temperature=0.9,
                response_format={"type": "json_object"},
            )
            .content
        )
        preferences = json.loads(preferences)["preferences"]
        # pick 4 random preferences
        preferences = rd.sample(preferences, 4)

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
        user.set_state_machine(sm)
        try:
            conv, rd_walk = user.generate_conversation(model, graph_description, seed)
            # save conversation in a file
            with open(f"generated_conv/{machine.__name__}_simulated_conversation.jsonl", "a") as f:
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
    args.add_argument("-m", "--machine", type=str)
    args = args.parse_args()
    machines = {"recipe": RecipeMachine, "car": RentCarMachine, "doctor": DoctorMachine, "hotel": HotelMachine, "worker": WorkerAgendaMachine}
    if args.machine not in machines:
        raise ValueError(f"Machine {args.machine} not found")
    DEBUG = args.debug
    main(
        machine=machines[args.machine],
        loop=args.num,
    )
