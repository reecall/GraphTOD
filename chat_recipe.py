from objects.recipe_machine import RecipeMachine
from dotenv import load_dotenv

load_dotenv(override=True)

sm = RecipeMachine(DEBUG=True)

while True:
    print(f"Agent: {sm.history[-1][1]}")
    print(f"Current state: {sm.state}")
    user_input = input("You: ")
    sm.history.append(("user", user_input))
    output = sm.get_response(user_input)
    if sm.state == "stop":
        print(f"Agent: {sm.history[-1][1]}")
        break
