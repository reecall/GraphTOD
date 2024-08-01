from objects import RecipeMachine, RentCarMachine, DoctorMachine
from dotenv import load_dotenv
import argparse

load_dotenv(override=True)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument(
    "-m",
    "--machine",
    help="Chat with the recipe machine",
)
args = parser.parse_args()

if args.machine == "recipe":
    sm = RecipeMachine(DEBUG=True)
elif args.machine == "car":
    sm = RentCarMachine(DEBUG=True)
elif args.machine == "doctor":
    sm = DoctorMachine(DEBUG=True)

while True:
    print(f"Agent: {sm.history[-1][1]}")
    print(f"Current state: {sm.state}")
    user_input = input("You: ")
    sm.history.append(("user", user_input))
    output = sm.get_response(user_input)
    if sm.state == "stop":
        print(f"Agent: {sm.history[-1][1]}")
        break
