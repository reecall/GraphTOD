# Unieval

Usage of Unieval[ https://arxiv.org/abs/2210.07197 ] for the evaluation of the generated conversations.

Code from the folder metrics: https://github.com/maszhongming/UniEval


## Explanation
Unieval is a T5-based model that can be used to evaluate the quality of the generated conversations. It uses the following metrics:
naturalness, coherence, understandability.

## Usage

```bash
python eval_conv.py -f conv.jsonl -t graphtod
```