import os
import jsonlines
import json
import argparse
from langchain.prompts import PromptTemplate
from nltk.app.wordnet_app import explanation
from tqdm import tqdm
from convertformat import extract_syntod_conv
from objects.AI_model import AIModel, get_ai_model
import pandas as pd
from langchain_community.chat_models.azureml_endpoint import (
    AzureMLChatOnlineEndpoint,
    CustomOpenAIChatContentFormatter,
)

HERE_PATH = os.path.dirname(os.path.realpath(__file__))


def evaluate_with_llm(conversation: str, conversation2):
    # Load prompt
    global HERE_PATH
    prompt = PromptTemplate.from_file(
        template_file=f"{HERE_PATH}/lmsys_for_conv.prompt",
        input_variables=["conversation"],
    )
    formatted_prompt = prompt.format(
        conversation=conversation, conversation2=str(conversation2)
    )

    # Load LLM
    ai_model: AIModel = get_ai_model()
    mistral_model: AIModel = get_ai_model()
    mistral_model.set_model("mistral")
    # cohere_model: AIModel = get_ai_model()
    # cohere_model.set_model("cohere")

    response = (
        ai_model()
        .invoke(
            formatted_prompt, temperature=0, response_format={"type": "json_object"}
        )
        .content
    )
    # print(response)

    response_mistral = (
        mistral_model()
        .invoke(
            formatted_prompt, temperature=0, response_format={"type": "json_object"}
        )
        .content
    )

    # response_cohere = (
    #     cohere_model()
    #     .invoke(
    #         formatted_prompt, temperature=0, response_format={"type": "json_object"}
    #     )
    #     .content
    # )

    # convert as json
    response = json.loads(response)
    response_mistral = json.loads(response_mistral)
    # response_cohere = json.loads(response_cohere)
    #
    jury1 = response["choice"]
    jury2 = response_mistral["choice"]
    # jury3 = response_cohere["choice"]
    #
    dict = {"[[A>>B]]": 1, "[[A>B]]": 2, "[[A=B]]": 3, "[[B>A]]": 4, "[[B>>A]]": 5}
    jury1 = dict[jury1]
    jury2 = dict[jury2]
    # jury3 = dict[jury3]
    mean_jury = (jury1 + jury2) / 2
    print("This is the mean of the jury : ", mean_jury)

    # TODO : mean of results for jury
    # mean = (jury1 + jury2 + jury3) / 3
    # print(mean)

    return response


def load_conversations(file_path: str):
    with jsonlines.open(file_path) as reader:
        conversations = [line for line in reader]
    return conversations


def format_conversation(conversation: dict, type: str = "graphtod"):
    if type == "graphtod":
        conversation = conversation["conversation"]
    formatted_conversation = ""
    for message in conversation:
        if type == "syntod":
            formatted_conversation += f"{message['speaker']}: {message['text']}\n"
        else:
            formatted_conversation += f"{message['role']}: {message['text']}\n"
    return formatted_conversation


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file", type=str, help="Path to the file with conversations", required=True
    )
    parser.add_argument(
        "--file2",
        type=str,
        help="Path to the file with conversations to compare to",
        required=True,
    )
    parser.add_argument(
        "-c", "--crop", type=int, help="Number of conversations to evaluate"
    )
    args = parser.parse_args()

    conversations = load_conversations(args.file)
    conversation2 = pd.read_json(args.file2, lines=True)
    choice = []
    explanation = []
    conv1 = []
    conv2 = []
    if args.crop:
        name = "results_recipe_crop_{}.csv".format(args.crop)
        print("Cropping conversations to", args.crop)
        conversations = conversations[: args.crop]

        for i in range(len(conversations)):
            if i < len(conversation2):
                conv_syntod = extract_syntod_conv(conversation2.iloc[i].text, "str")
                a = format_conversation(conv_syntod, "syntod")
                e = evaluate_with_llm(
                    format_conversation(conversations[i]),
                    format_conversation(conv_syntod, "syntod"),
                )
                # TODO : avoir une sortie avec champs "choice" et "explanation"
                choice.append(e["choice"])
                explanation.append(e["explanation"])
                conv1.append(format_conversation(conversations[i]))
                conv2.append(a)

            else:
                res = {
                    choice: choice,
                    explanation: explanation,
                    conv1: conv1,
                    conv2: conv2,
                }
                df = pd.DataFrame(res)
                df.to_csv(
                    name,
                    mode="a",
                    header=not os.path.exists(name),
                )
                print("result saved in : {} \n".format(name))
                break
        res = {
            "choice": choice,
            "explanation": explanation,
            "conv1": conv1,
            "conv2": conv2,
        }
        df = pd.DataFrame(res)
        print(df)
        df.to_csv(
            name,
            mode="a",
            header=not os.path.exists(name),
        )
        print("result saved in : {} \n".format(name))

    else:
        name = "results_recipe.csv"
        for i in range(len(conversations)):
            conv_syntod = extract_syntod_conv(conversation2.iloc[i].text, "str")
            a = format_conversation(conv_syntod, "syntod")
            e = evaluate_with_llm(
                format_conversation(conversations[i]),
                format_conversation(conv_syntod, "syntod"),
            )
            choice.append(e["choice"])
            explanation.append(e["explanation"])
            conv1.append(format_conversation(conversations[i]))
            conv2.append(a)
        res = {
            "choice": choice,
            "explanation": explanation,
            "conv1": conv1,
            "conv2": conv2,
        }
        df = pd.DataFrame(res)
        df.to_csv(name, mode="a", header=not os.path.exists(name))
        print("result saved in : {} \n".format(name))
