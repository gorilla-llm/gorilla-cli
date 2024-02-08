import os
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import json
from pprint import pprint
from openai import OpenAI

def get_bash_history():
    history_file = os.path.expanduser("~/.bash_history")
    prev_operations = ""
    try:
        with open(history_file, "r") as file:
            history = file.readlines()
    except FileNotFoundError:
        return "No bash history was found."
    return history[:-10]


def anonymize_bash_history(operations):
    analyzer = AnalyzerEngine()
    analyzer_results = analyzer.analyze(text=operations, language="en")
    anonymizer = AnonymizerEngine()
    anonymized_results = anonymizer.anonymize(
        text=operations, analyzer_results=analyzer_results
    )
    return anonymized_results.text


def remove_duplicates(operations: list[str]):
    return list(set(operations))


def stringify_bash_history(operations: list[str]):
    return "\n".join(operations)


def synthesize_bash_history(client, desired_operation, gorila_history, history):
    SYSTEM_PROMPT = """
You are an assistant for a developer who wants to find the right API call for a specific task. 
The developer has bash history that contains the command they used to perform a task.
Synthesize their bash history to provide the API call prediction model with extra context about the task.
For reference, the API call prediction model, called Gorilla, is trained on a large dataset of API calls and their associated tasks.
You may see the developer's previous operations with the API calling tool in their bash history.
Use the previous bash history as well as their query to provide the model with a short paragraph of possible relevant context.
There is a chance that their query has nothing to do with the bash history, so in that case, return 'No relevant context found'.
"""
    USER_PROMPT = f"""
The user's bash history is:
{history}

The user's previous operations with the API calling tool are:
{gorila_history}

The query of the user is:
{desired_operation}

Use this information to provide the model with a short paragraph of possible relevant context.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    return response.choices[0].message.content


def personalize(query, gorilla_history, open_ai_key, pi_removal=True):
    history = stringify_bash_history(remove_duplicates(get_bash_history()))
    client = OpenAI(api_key=open_ai_key)
    if pi_removal:
        history = anonymize_bash_history(history)
    summary = synthesize_bash_history(client, query, gorilla_history, history)
    return summary
