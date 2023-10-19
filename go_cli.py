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
import requests
import subprocess
import argparse
import urllib.parse
import sys
from halo import Halo
import go_questionary

__version__ = "0.0.10"  # current version
SERVER_URL = "https://cli.gorilla-llm.com"
UPDATE_CHECK_FILE = os.path.expanduser("~/.gorilla-cli-last-update-check")
USERID_FILE = os.path.expanduser("~/.gorilla-cli-userid")
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


def check_for_updates():
    # Check if a new version of gorilla-cli is available once a day
    try:
        with open(UPDATE_CHECK_FILE, "r") as f:
            last_check_date = datetime.datetime.strptime(f.read(), "%Y-%m-%d")
    except FileNotFoundError:
        last_check_date = datetime.datetime.now() - datetime.timedelta(days=1)
    if datetime.datetime.now() - last_check_date >= datetime.timedelta(days=1):
        try:
            response = requests.get("https://pypi.org/pypi/gorilla-cli/json")
            latest_version = response.json()["info"]["version"]

            if latest_version > __version__:
                print(f"A new version is available: {latest_version}. Update with `pip install --upgrade gorilla-cli`")
        except Exception as e:
            print("Unable to check for updates:", e)
        try:
            with open(UPDATE_CHECK_FILE, "w") as f:
                f.write(datetime.datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            print("Unable to write update check file:", e)


def get_user_id():
    # Unique user identifier for authentication and load balancing
    # Gorilla-CLI is hosted by UC Berkeley Sky lab for FREE as a
    #  research prototype. Please don't spam the system or use it
    #  for commercial serving. If you would like to request rate
    #  limit increases for your GitHub handle, please raise an issue.
    try:
        with open(USERID_FILE, "r") as f:
            user_id = str(f.read())
            # If file found and user_id is blank. User hasn't setup github
            if user_id == "":
                user_id = str(uuid.uuid4())
        return user_id
    except FileNotFoundError:
        # First time
        try:
            user_id = (
                subprocess.check_output(["git", "config", "--global", "user.email"])
                .decode("utf-8")
                .strip()
            )
            print(WELCOME_TEXT)
            response = (
                input(f"Use your Github handle ({user_id}) as user id? [Y/n]: ")
                .strip()
                .lower()
            )
            if response in ["n", "no"]:
                user_id = str(uuid.uuid4())
        except Exception as e:
            # If git not installed then generate and use a random user id
            issue_title = urllib.parse.quote(
                f"Problem with generating userid from GitHub: {str(e)}"
            )
            issue_body = urllib.parse.quote(f"Unable to generate userid: {str(e)}")
            print(
                f"Git not installed or not configured, so cannot import userid from Git.\nTry running \
                  \n\ngit config --global user.email <your_email>\n\nPlease run 'gorilla <command>' again after initializing git. \n Will use a random user-id. If the problem persists, please raise an issue: \
                  \n{ISSUE_URL}?title={issue_title}&body={issue_body}"
            )
            user_id = str(uuid.uuid4())
            print(WELCOME_TEXT)

        try:
            # Write user_id to file
            with open(USERID_FILE, "w") as f:
                f.write(user_id)
            return user_id
        except Exception as e:
            issue_title = urllib.parse.quote("Problem with userid file")
            issue_body = urllib.parse.quote(f"Unable to write userid file: {str(e)}")
            print("Unable to write userid to file:", e)
            print(
                f"Try deleting USERID_FILE and run 'gorilla <command>' again. If the problem persists, please raise an issue:\
                   {ISSUE_URL}?title={issue_title}&body={issue_body}"
            )
            print(
                f"Using a temporary UID {user_id} for now.."
            )
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


def main():
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

    def get_history_commands(history_file):
        """
        Takes in history file
        Returns None if file doesn't exist or empty
        Returns list of last 10 history commands in the file if it exists
        """
        if os.path.isfile(history_file):
            with open(history_file, 'r') as history:
                lines = history.readlines()
                if not lines:
                    print("No command history.")
                return lines[-HISTORY_LENGTH:]
        else:
            print("No command history.")
            return

    args = sys.argv[1:]
    user_input = " ".join(args)
    user_id = get_user_id()


    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Gorilla CLI Help Doc")
    parser.add_argument("-p", "--history", action="store_true", help="Display command history")
    parser.add_argument("command_args", nargs='*', help="Prompt to be inputted to Gorilla")

    args = parser.parse_args()

    # Generate a unique interaction ID
    interaction_id = str(uuid.uuid4())

    if args.history:
        commands = get_history_commands(HISTORY_FILE)
    else:
        with Halo(text=f"{GORILLA_EMOJI}Loading", spinner="dots"):
            try:
                data_json = {
                    "user_id": user_id,
                    "user_input": user_input,
                    "interaction_id": interaction_id,
                }
                response = requests.post(
                    f"{SERVER_URL}/commands", json=data_json, timeout=30
                )
                commands = response.json()
            except requests.exceptions.RequestException as e:
                print("Server is unreachable.")
                print("Try updating Gorilla-CLI with 'pip install --upgrade gorilla-cli'")
                return

    check_for_updates()

    if commands:
        selected_command = go_questionary.select(
            "", choices=commands, instruction="Welcome to Gorilla. Use arrow keys to select. Ctrl-C to Exit"
        ).ask()

        if not selected_command:
            # happens when Ctrl-C is pressed
            return
        exit_condition = execute_command(selected_command)

        # Commands failed / succeeded?
        try:
            response = requests.post(
                f"{SERVER_URL}/command-execution-result",
                json={
                    "user_id": user_id,
                    "command": selected_command,
                    "exit_condition": exit_condition,
                    "interaction_id": interaction_id,
                },
                timeout=30,
            )
            if response.status_code != 200:
                print("Failed to send command execution result to the server.")
        except requests.exceptions.Timeout:
            print("Failed to send command execution result to the server: Timeout.")


if __name__ == "__main__":
    main()
