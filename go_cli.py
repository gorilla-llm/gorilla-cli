# Copyright 2023 https://github.com/ShishirPatil/gorilla
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import sys
import uuid
import fcntl
import platform
import requests
import click
import json
import subprocess
import termios
import urllib.parse
import sys
from halo import Halo
import go_questionary

__version__ = "0.0.11"  # current version
SERVER_URL = "https://cli.gorilla-llm.com"
CONFIG_FILE = "./config.json"#os.path.expanduser("~/.gorilla-cli-config.json")
HISTORY_FILE = os.path.expanduser("~/.gorilla_cli_history")
ISSUE_URL = f"https://github.com/gorilla-llm/gorilla-cli/issues/new"
GORILLA_EMOJI = "🦍 " if go_questionary.try_encode_gorilla() else ""
HISTORY_LENGTH = 10
WELCOME_TEXT = f"""===***===
{GORILLA_EMOJI}Welcome to Gorilla-CLI! Enhance your Command Line with the power of LLMs! 

Simply use `gorilla <your desired operation>` and Gorilla will do the rest. For instance:
    gorilla generate 100 random characters into a file called test.txt
    gorilla get the image ids of all pods running in all namespaces in kubernetes
    gorilla list all my GCP instances

A research prototype from UC Berkeley, Gorilla-CLI ensures user control and privacy:
 - Commands are executed only with explicit user approval.
 - While queries and error (stderr) logs are used to refine our model, we NEVER gather output (stdout) data.

Visit github.com/gorilla-llm/gorilla-cli for examples and to learn more!
===***==="""


def generate_random_uid():
    return str(uuid.uuid4())

def get_git_email():
    return subprocess.check_output(["git", "config", "--global", "user.email"]).decode("utf-8").strip()

def get_system_info():
    return platform.system()

def append_to_bash_history(selected_command):
    try:
        with open(os.path.expanduser("~/.bash_history"), "a") as history_file:
            history_file.write(selected_command + '\n')
    except Exception as e:
        pass




def prefill_shell_cmd(cmd):
    # Inspired from 
    stdin = 0
    # Save TTY attributes for stdin
    oldattr = termios.tcgetattr(stdin)
    # Create new attributes to fake input
    newattr = termios.tcgetattr(stdin)
    # Disable echo in stdin -> only inject cmd in stdin queue (with TIOCSTI)
    newattr[3] &= ~termios.ECHO
    # Enable non-canonical mode -> ignore special editing characters
    newattr[3] &= ~termios.ICANON
    # Use the new attributes
    termios.tcsetattr(stdin, termios.TCSANOW, newattr)
    # Write the selected command in stdin queue
    for c in cmd:
        fcntl.ioctl(stdin, termios.TIOCSTI, c)
    # Restore TTY attributes for stdin
    termios.tcsetattr(stdin, termios.TCSADRAIN, oldattr)


def raise_issue(title, body):
    issue_title = urllib.parse.quote(title)
    issue_body = urllib.parse.quote(body)
    issue_url = f"{ISSUE_URL}?title={issue_title}&body={issue_body}"
    print(f"If the problem persists, please raise an issue: {issue_url}")

def check_for_updates():
    # Check if a new version of gorilla-cli is available once a day
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)
    except Exception as e:
            config_json = {}
        
    if "last_check_date" in config_json:
        last_check_date = datetime.datetime.strptime(config_json["last_check_date"], "%Y-%m-%d")
    else:
        last_check_date = datetime.datetime.now() - datetime.timedelta(days=1)
    
    if datetime.datetime.now() - last_check_date >= datetime.timedelta(days=1):
        try:
            response = requests.get("https://pypi.org/pypi/gorilla-cli/json")
            latest_version = response.json()["info"]["version"]

            if latest_version > __version__:
                print(f"A new version is available: {latest_version}. Update with `pip install --upgrade gorilla-cli`")
        except Exception as e:
            print("Unable to check for updates:", e)

    config_json["last_check_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config_json, config_file)


def get_user_id():
    # Unique user identifier for authentication and load balancing
    # Gorilla-CLI is hosted by UC Berkeley Sky lab for FREE as a
    #  research prototype. Please don't spam the system or use it
    #  for commercial serving. If you would like to request rate
    #  limit increases for your GitHub handle, please raise an issue.
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)
    except Exception as e:
        config_json = {}

    if "user_id" in config_json:
            return config_json["user_id"]
        
    try:
        user_id = get_git_email()
        response = (
            input(f"Use your Github handle ({user_id}) as user id? [Y/n]: ")
            .strip()
            .lower()
        )
        if response in ["n", "no"]:
            user_id = generate_random_uid()
        else:
            print(WELCOME_TEXT)
            config_json["user_id"] = user_id
            with open(CONFIG_FILE, "w") as config_file:
                config_json = json.dump(config_json, config_file)

    except Exception as e:
        print(e)
        # If git not installed then generate and use a random user id
        print(f"Unable to import userid from Git. Git not installed or git user.email not configured.")
        print(f"Will use a random user-id. \n")
        user_id = generate_random_uid()
    
    return user_id

def format_command(input_str):
    """
    Standardize commands to be stored with a newline
    character in the history
    """
    if not input_str.endswith('\n'):
        input_str += '\n'
    return input_str

def append_string_to_file_if_missing(file_path, target_string):
    """
    Don't append command to history file if it already exists.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Check if the target string is already in the file
        if target_string not in lines[-HISTORY_LENGTH:]:
            with open(file_path, 'a') as file:
                file.write(target_string)
    except FileNotFoundError:
        # If the file doesn't exist, create it and append the string
        with open(file_path, 'w') as file:
            file.write(target_string)


def specify_models(ctx, param, file_path):
    # By default, Gorilla-CLI combines the capabilities of multiple Language Learning Models.
    # The specify_models command will make Gorilla exclusively utilize the inputted models.
    if not file_path or ctx.resilient_parsing:
        return
    try:
        with open(file_path, "r") as models_file:
            models_json = json.load(models_file)
    except Exception as e:
        print("Failed to read from " + file_path)
        ctx.exit()
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)
    except Exception as e:
        config_json = {}
    config_json["models"] = models_json["models"]
    with open(CONFIG_FILE, "w") as config_file:
        json.dump(config_json, config_file)
        print("models set to: " + str(config_json["models"]))

    ctx.exit()


def reset_models(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)
        if "models" in config_json:
            del config_json["models"]
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(config_json, config_file)
    except Exception as e:
        pass
    ctx.exit()


def execute_command(cmd):
    cmd = format_command(cmd)
    process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

    save = not cmd.startswith(':')
    if save:
        append_string_to_file_if_missing(HISTORY_FILE, cmd)

    error_msg = process.stderr.decode("utf-8", "ignore")
    if error_msg:
        print(f"{error_msg}")
        return error_msg
    return str(process.returncode)

def load_config():
    # Load the user's configuration file and perform any necessary checks
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)
    return config_json


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()
    
def get_history_commands(ctx, param, value):
    """
    Takes in history file
    Returns None if file doesn't exist or empty
    Returns list of last 10 history commands in the file if it exists
    """
    if not value or ctx.resilient_parsing:
        return
    history_file = HISTORY_FILE
    if os.path.isfile(history_file):
        with open(history_file, 'r') as history:
            lines = history.readlines()
            if not lines:
                click.echo("No command history.")
            else:
                click.echo(lines[-HISTORY_LENGTH:])
    else:
        click.echo("No command history.")
    ctx.exit()

def format_output_commands(commands):
    for i, command in enumerate(commands):
        if command[-1] == '\n':
            commands[i] = command[:-1]
            break
    return commands

    

@click.command()
@click.option('--user_id', '--u', default=get_user_id(), help="User id [default: 'git config --global user.email' OR random uuid]")
@click.option('--server', default = SERVER_URL, help = "LLM host [default: 'cli.gorilla-llm.com']")
@click.option('--set_models', type=click.Path(), callback = specify_models, expose_value=True,
              help = "Make Gorilla exclusively utilize the models in the json file specified")
@click.option('--reset_models', is_flag=True, callback =reset_models, expose_value=False, is_eager=True,
              help = "Reset models configuration")
@click.option('--model', '-m', help = "Prompt Gorilla CLI to only use the specified model")
@click.option('--version', help = "Return the version of GORILLA_CLI", is_flag=True, callback= print_version, expose_value=False, is_eager=True)
@click.option('--history', help = "Display command history", is_flag=True, callback= get_history_commands, expose_value=False, is_eager=True)
@click.argument('prompt', nargs = -1)
def main(
    user_id,
    server,
    model,
    set_models,
    prompt,
):
    check_for_updates()
    config = load_config()

    if len(prompt) == 0:
        print("error: prompt not found, see gorilla-cli usage below " + "➡️")
        with click.Context(main) as ctx:
            click.echo(main.get_help(ctx))
        return

    #Check if the user has specific model preference.
    if model:
        chosen_models = model
    elif "models" in config:
        chosen_models = config["models"]
    else:
        chosen_models = None

    # Generate a unique interaction ID
    interaction_id = str(uuid.uuid4())

    args = sys.argv[1:]
    user_input = " ".join(args)
    system_info = get_system_info()
    data_json = {
                "user_id": user_id,
                "user_input": user_input,
                "interaction_id": interaction_id,
                "system_info": system_info
            }
    if chosen_models:
        data_json["models"] = chosen_models
        print("Results are only chosen from the following LLM model(s): ", chosen_models)

    with Halo(text=f"{GORILLA_EMOJI}Loading", spinner="dots"):
        try:
            response = requests.post(
                f"{server}/commands", json=data_json, timeout=30
            )
            commands = response.json()
        except requests.exceptions.RequestException as e:
            print("\nServer " + server + " is unreachable.")
            print("Try updating Gorilla-CLI with 'pip install --upgrade gorilla-cli'")
            return

    if commands:
        commands = format_output_commands(commands)
        selected_command = go_questionary.select(
            "", choices=commands, instruction="Welcome to Gorilla. Use arrow keys to select. Ctrl-C to Exit"
        ).ask()

        if not selected_command:
            # happens when Ctrl-C is pressed
            return
        
        # Append command to bash history
        if system_info == "Linux":
            append_to_bash_history(selected_command)
            prefill_shell_cmd(selected_command)

        exit_condition = execute_command(selected_command)
        json = {
                "user_id": user_id,
                "command": selected_command,
                "exit_condition": exit_condition,
                "interaction_id": interaction_id,
            }
        
        # Commands failed / succeeded?
        try:
            response = requests.post(
                f"{server}/command-execution-result",
                json=json,
                timeout=30,
            )
            if response.status_code != 200:
                print("Failed to send command execution result to the server.")
        except requests.exceptions.Timeout:
            print("Failed to send command execution result to the server: Timeout.")

if __name__ == "__main__":
    main()
