from go_questionary.prompts import autocomplete
from go_questionary.prompts import confirm
from go_questionary.prompts import text
from go_questionary.prompts import select
from go_questionary.prompts import rawselect
from go_questionary.prompts import password
from go_questionary.prompts import checkbox
from go_questionary.prompts import path

AVAILABLE_PROMPTS = {
    "autocomplete": autocomplete.autocomplete,
    "confirm": confirm.confirm,
    "text": text.text,
    "select": select.select,
    "rawselect": rawselect.rawselect,
    "password": password.password,
    "checkbox": checkbox.checkbox,
    "path": path.path,
    # backwards compatible names
    "list": select.select,
    "rawlist": rawselect.rawselect,
    "input": text.text,
}


def prompt_by_name(name):
    return AVAILABLE_PROMPTS.get(name)
