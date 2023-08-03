# noinspection PyUnresolvedReferences
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.styles import Style

import go_questionary.version
from go_questionary.form import Form
from go_questionary.form import form
from go_questionary.prompt import prompt, unsafe_prompt
from go_questionary.prompts.common import Choice
from go_questionary.prompts.common import Separator
from go_questionary.prompts.common import print_formatted_text as print
from go_questionary.question import Question

# import the shortcuts to create single question prompts
from go_questionary.prompts.autocomplete import autocomplete
from go_questionary.prompts.select import select
from go_questionary.prompts.checkbox import checkbox
from go_questionary.prompts.text import text
from go_questionary.prompts.path import path
from go_questionary.prompts.confirm import confirm
from go_questionary.prompts.password import password
from go_questionary.prompts.rawselect import rawselect

# Utilities
from go_questionary.utils import try_encode_gorilla

__version__ = go_questionary.version.__version__

__all__ = [
    "__version__",
    # question types
    "autocomplete",
    "checkbox",
    "confirm",
    "password",
    "path",
    "rawselect",
    "select",
    "text",
    # utility methods
    "print",
    "form",
    "prompt",
    "unsafe_prompt",
    # commonly used classes
    "Form",
    "Question",
    "Choice",
    "Style",
    "Separator",
    "Validator",
    "ValidationError",
    "try_encode_gorilla"
]
