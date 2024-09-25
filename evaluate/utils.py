import os
import jsonlines
import json
import argparse
from langchain.prompts import PromptTemplate
from tqdm import tqdm

from objects.AI_model import AIModel, get_ai_model

HERE_PATH = os.path.dirname(os.path.realpath(__file__))


def evaluate_with_llm(conversation: str):
    # Load prompt
    global HERE_PATH
    prompt = PromptTemplate.from_file(
        template_file=f"{HERE_PATH}/evaluator.prompt",
        input_variables=["conversation"],
    )
    formatted_prompt = prompt.format(conversation=conversation)

    # Load LLM
    ai_model: AIModel = get_ai_model()
    response = (
        ai_model()
        .invoke(
            formatted_prompt, temperature=0, response_format={"type": "json_object"}
        )
        .content
    )

    # convert as json
    response = json.loads(response)

    return response


def load_conversations(file_path: str):
    with jsonlines.open(file_path) as reader:
        conversations = [line for line in reader]
    return conversations


def format_conversation(conversation: dict):
    conversation = conversation["conversation"]
    formatted_conversation = ""
    for message in conversation:
        formatted_conversation += f"{message['role']}: {message['text']}\n"
    return formatted_conversation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", type=str, help="Path to the file with conversations", required=True
    )
    args = parser.parse_args()

    conversations = load_conversations(args.file)

    for conversation in tqdm(conversations[:3]):
        print(evaluate_with_llm(conversation))
        print("\n")
