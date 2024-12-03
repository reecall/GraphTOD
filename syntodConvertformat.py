import pandas as pd
import re


def extract_syntod_conv(conversation, mode="df"):
    # Extracting the conversation and intents
    pattern = r"(### HUMAN:|### ASSISTANT:|## \{.*?\})"  # Pattern to identify speaker and intents
    split_conversation = re.split(
        pattern, conversation
    )  # Split the conversation by pattern

    # Processing the split text into utterances and intents
    data = []
    current_speaker = None

    for part in split_conversation:
        part = part.strip()

        if part.startswith("### HUMAN:"):
            current_speaker = "HUMAN"
        elif part.startswith("### ASSISTANT:"):
            current_speaker = "ASSISTANT"
        elif part.startswith("## {"):
            intent_match = re.search(r'"intent":\s*"([^"]+)"', part)
            if intent_match:
                intent = intent_match.group(1)
                if data:  # Add intent to the last row (latest message)
                    data[-1]["intent"] = intent
        elif part.startswith("### RESULTS") or part.startswith("### RECIPE"):
            pass
        elif part.startswith("### SUGGESTIONS"):
            pass
        else:
            if part and current_speaker:  # Add utterance and speaker to data
                data.append(
                    {
                        "text": re.sub(r"[^a-zA-Z]+", " ", part),
                        "speaker": current_speaker,
                        "intent": None,
                    }
                )

    if mode == "df":
        df = pd.DataFrame(data)
        return df

    if mode == "str":
        return data  # TODO : careful with this


# conv = pd.read_json("generated_conv/train_recipe_original_syntod.jsonl", lines=True)
# uneconv = extract_syntod_conv(conv.iloc[16].text, "str")
# print(uneconv)
# print(uneconv[0])
#
# for i in range(len(uneconv)):
#     print(uneconv.loc[i].text)
#     print("next sentence \n")
