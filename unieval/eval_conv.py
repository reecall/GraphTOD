import argparse
import os
from sympy import evaluate
import nltk
from pathlib import Path

from unieval.utils import convert_to_json
from unieval.evaluator import get_evaluator

# from utils import convert_to_json
# from evaluator import get_evaluator
import pandas as pd

# needed at the setup of the repo
## EVAL WON'T WORK IF YOU DON'T HAVE THAT
nltk.download("punkt")
nltk.download("punkt_tab")

task = "dialogue"


def extract_whole_conv(conv, mode="graphtod"):
    """
    :param conv:
    :param mode: graphtod
    :return:
    """
    # tout le dialogue petit à petit
    # [ ut1, contexte1, out1+1;  ut1+ut2, contexte2, out2+1, ...]
    src_list = []
    output_list = []
    context_list = []
    for i in range(len(conv) - 1):
        if i == 0:
            src_list.append(conv.loc[i].text)
            output_list.append(conv.loc[i + 1].text)
        else:
            source = src_list[-1] + "\n" + conv.loc[i].text
            src_list.append(source)
            output = conv.loc[
                i + 1
            ].text  # avant j'avais output_list[-1] + conv.loc[i+1].text
            output_list.append(output)

        if mode == "graphtod":
            context_list.append(str(conv.loc[i + 1].state))
    return src_list, output_list, context_list


# src_list, output_list, context_list = extract_whole_conv(conv, mode = "graphtod")


def extract_utterances(conv, mode="graphtod"):
    # chaque utterance avec un historique uniquement de la phrase précédente (contexte : intent ou state)
    src_list = []
    output_list = []
    context_list = []
    for i in range(len(conv) - 1):
        if mode == "graphtod":
            context_list.append(str(conv.loc[i + 1].state))
        output_list.append(conv.loc[i + 1].text)
        src_list.append(conv.loc[i].text)

    return src_list, output_list, context_list


def launch_eval(conv, mode="utterance", type="graphtod", dims=None):
    """
    eval with utterances or whole conversation in history
    :param conv:
    :param mode:
    :return:
    """
    if dims is None:
        dims = ["naturalness", "coherence", "understandability"]
    if mode == "utterance":
        src_list, output_list, context_list = extract_utterances(conv, type)
    if mode == "full":
        src_list, output_list, context_list = extract_whole_conv(conv, type)

    data = convert_to_json(
        output_list=output_list, src_list=src_list, context_list=context_list
    )
    # print(data)
    evaluator = get_evaluator("dialogue")
    eval_scores = evaluator.evaluate(data, dims=dims)
    return eval_scores


def mean_scores(eval_scores, dims):
    """
    mean score to eval one full conversation
    :param eval_scores:
    :return:
    """
    # res = {'naturalness': [], 'coherence': [], 'engagingness': [], 'groundedness': [], 'understandability': [], 'overall': []}
    res = {k: [] for k in dims}
    res["overall"] = []
    for i in eval_scores:
        # print(i)
        for k, v in i.items():
            res[k].append(v)
    for k in res:
        res[k] = sum(res[k]) / len(res[k])
    return res


def eval_dataset(convs, mode="utterance", type="graphtod", dims=None):
    """
    eval a full dataset of conversations
    :param convs:
    :param mode:
    :return:
    """
    # res = {'naturalness': [], 'coherence': [], 'engagingness': [], 'groundedness': [], 'understandability': [], 'overall': []}
    res = {k: [] for k in dims}
    res["overall"] = []
    invalid_conv = 0
    for i in range(len(convs)):
        print("conversation i: ", i)
        if type == "graphtod":
            conv = convs[i]
        try:
            eval_scores = launch_eval(conv, mode, type, dims)
            mss = mean_scores(eval_scores, dims)
            for k in mss:
                res[k].append(mss[k])
        except RuntimeError:
            invalid_conv += 1
            print("The conversation is not valid and will not be evaluated")

    if res:
        for k in res:
            res[k] = sum(res[k]) / len(res[k])
        print("The dataset has ", invalid_conv, " invalid conversations")
        res["invalid_conv"] = invalid_conv
        res["mode"] = mode
        res["nb_conv"] = len(convs)
        return res
    return "No valid conversation"


def save_res(res, type, filename, dims):
    """
    save the results of the evaluation with unieval
    """
    if res == "No valid conversation":
        print("No valid conversation to save")
    name = "EVAL_" + type + ".csv"
    filepath = Path("results/{}".format(name))
    res["filename"] = filename
    res["dims"] = str(dims)
    df = pd.DataFrame(res, index=[0])
    df.to_csv(filepath, mode="a", header=not os.path.exists(filepath))


def unieval_eval(file, dims, mode="utterance", type="graphtod"):
    data = pd.read_json(file, lines=True)
    list_conv = list(map(lambda x: pd.json_normalize(x), data.conversation))
    evaluate = eval_dataset(list_conv, mode=mode, type=type, dims=dims)
    return evaluate


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-f", "--file", type=str)
    args.add_argument("-m", "--mode", type=str, default="full")
    args.add_argument("-t", "--type", type=str, default="graphtod")
    args.add_argument(
        "-d",
        "--dims",
        type=str,
        default=["naturalness", "coherence", "understandability"],
    )
    args = args.parse_args()

    # load data and evaluate full dataset

    if args.type == "graphtod":
        data = pd.read_json(args.file, lines=True)
        list_conv = list(map(lambda x: pd.json_normalize(x), data.conversation))
        evaluate = eval_dataset(
            list_conv[0:1], mode=args.mode, type=args.type, dims=args.dims
        )

    save_res(evaluate, args.type, args.file, args.dims)
    print(evaluate)
