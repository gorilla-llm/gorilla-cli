import os
from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import json
from pprint import pprint
from openai import OpenAI
from personalization.prompts import get_system_prompt, get_user_prompt

class GorillaPersonalizer:
    """A class to personalize the user's bash history and query to provide the model with relevant context.

    Attributes:
    client: The OpenAI client.

    """

    def __init__(self, open_ai_key):
        """ Initializes the GorillaPersonalizer class."""
        self.client = OpenAI(api_key=open_ai_key)

    def get_bash_history(self):
        """
        Retrieves the user's bash history. (Last 10 commands)
        """
        history_file = os.path.expanduser("~/.bash_history")
        prev_operations = ""
        try:
            with open(history_file, "r") as file:
                history = file.readlines()
        except FileNotFoundError:
            return "No bash history was found."
        return history[:-10]

    def anonymize_bash_history(self, operations):
        """
        Uses Microsoft's Presidio to anonymize the user's bash history.

        Args:
        operations: The user's bash history.

        """
        analyzer = AnalyzerEngine()
        analyzer_results = analyzer.analyze(text=operations, language="en")
        anonymizer = AnonymizerEngine()
        anonymized_results = anonymizer.anonymize(
            text=operations, analyzer_results=analyzer_results
        )
        return anonymized_results.text

    def remove_duplicates(self, operations: list[str]):
        """Removes duplicates from the user's bash history

        Args:
            operations: The user's bash history.

        """
        return list(set(operations))

    def stringify_bash_history(self, operations: list[str]):
        """Stringifies the user's bash history.

        Args:
            operations: The user's bash history.

        """
        return "\n".join(operations)

    def synthesize_bash_history(self, desired_operation, gorilla_history, history):
        """Uses OpenAI api to synthesize the user's bash, gorilla history.
        It synthesizes this history with the current operation in mind, with the goal of providing the model with relevant context.

        Args:
            client: The OpenAI client.
            desired_operation: The operation the user wants to perform.
            gorilla_history: The user's previous operations with the Gorilla
            history: The user's bash history.

        """
        system_prompt = get_system_prompt()
        user_prompt = get_user_prompt(history, gorilla_history, desired_operation)
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    def personalize(self, query, gorilla_history, pi_removal=True):
        """Personalizes the user's bash history and query to provide the model with relevant context.

        Args:
            query: The operation the user wants to perform.
            gorila_history: The user's previous operations with the Gorilla
            open_ai_key: The OpenAI API key.
            pi_removal: Whether to remove personally identifiable information from the user's bash history.

        """

        print ("PERSONALIZING YOUR STUFF")
        history = self.stringify_bash_history(self.remove_duplicates(self.get_bash_history()))
        if pi_removal:
            history = self.anonymize_bash_history(history)
        summary = self.synthesize_bash_history(query, gorilla_history, history)
        return summary
