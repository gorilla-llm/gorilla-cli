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
import json
import io
import subprocess
import urllib.parse
import sys
from halo import Halo
import go_questionary

__version__ = "0.0.10"  # current version
SERVER_URL = "https://cli.gorilla-llm.com"
CONFIG_FILE = os.path.expanduser("~/.gorilla-cli-config.json")
ISSUE_URL = f"https://github.com/gorilla-llm/gorilla-cli/issues/new"
GORILLA_EMOJI = "🦍 " if go_questionary.try_encode_gorilla() else ""
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


def check_for_updates(last_check_date):
    # Check if a new version of gorilla-cli is available once a day
    if datetime.datetime.now() - last_check_date >= datetime.timedelta(days=1):
        try:
            response = requests.get("https://pypi.org/pypi/gorilla-cli/json")
            latest_version = response.json()["info"]["version"]

            if latest_version > __version__:
                print(f"A new version is available: {latest_version}. Update with `pip install --upgrade gorilla-cli`")
        except Exception as e:
            print("Unable to check for updates:", e)


def get_user_id():
    # Unique user identifier for authentication and load balancing
    # Gorilla-CLI is hosted by UC Berkeley Sky lab for FREE as a
    #  research prototype. Please don't spam the system or use it
    #  for commercial serving. If you would like to request rate
    #  limit increases for your GitHub handle, please raise an issue.

    authenticated = False
    try:
        user_id = (
            subprocess.check_output(["git", "config", "--global", "user.email"])
            .decode("utf-8")
            .strip()
        )
        response = (
            input(f"Use your Github handle ({user_id}) as user id? [Y/n]: ")
            .strip()
            .lower()
        )
        if response in ["n", "no"]:
            user_id = str(uuid.uuid4())
        else:
            authenticated = True
    except Exception as e:
        # If git not installed then generate and use a random user id
        issue_title = urllib.parse.quote(
            f"Problem with generating userid from GitHub: {str(e)}"
        )
        issue_body = urllib.parse.quote(f"Unable to generate userid: {str(e)}")
        print(
            f"Git not installed, so cannot import userid from Git. \n Please run 'gorilla <command>' again after initializing git. \n Will use a random user-id. If the problem persists, please raise an issue: \
                {ISSUE_URL}?title={issue_title}&body={issue_body}"
        )
        user_id = str(uuid.uuid4())
    
    return (user_id, authenticated)

def specify_models(file):
    # By default, Gorilla-CLI combines the capabilities of multiple Language Learning Models.
    # The specify_models command will make Gorilla exclusively utilize the inputted models.
    try:
        with open(CONFIG_FILE, "r+") as config_file:
            config_json = json.load(config_file)
            config_json["models"] = models
            json.dump(config_json, config_file)
    except io.UnsupportedOperation:
        print("Config.json has not been initialized")


def execute_command(cmd):
        process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        error_msg = process.stderr.decode("utf-8", "ignore")
        if error_msg:
            print(f"{error_msg}")
            return error_msg
        return str(process.returncode)

def load_config():
    # Load the user's configuration file and perform any necessary checks
    config_json = {}
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as config_file:
            config_json = json.load(config_file)

    if "last_check_date" in config_json:
        last_check_date = datetime.datetime.strptime(config_json["last_check_date"], "%Y-%m-%d")
    else:
        last_check_date = datetime.datetime.now() - datetime.timedelta(days=1)
    check_for_updates(last_check_date)
    config_json["last_check_date"] = datetime.datetime.now().strftime("%Y-%m-%d")

    # Check for user_id. Only add new user_id to the config file if the user has been authenticated.
    user_id = config_json["user_id"]
    if "user_id" not in config_json:
        user_id, authenticated = get_user_id()
        if authenticated:
            config_json["user_id"] = user_id
    
    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(json.dumps(config_json))

    config_json["user_id"] = user_id

    return config_json

def main():
    config = load_config()

    args = sys.argv[1:]
    if args[0] == "--model":
        if len(args) != 2:
            print('--model command must follow the following format: gorilla --model <file path>')
            return
        specify_models[args[1]]

    user_input = " ".join(args)

    # Generate a unique interaction ID
    interaction_id = str(uuid.uuid4())

    with Halo(text=f"{GORILLA_EMOJI}Loading", spinner="dots"):
        try:
            data_json = {
                "user_id": config["user_id"],
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

    print(WELCOME_TEXT)
    
    if commands:
        selected_command = go_questionary.select(
            "", choices=commands, instruction=""
        ).ask()
        exit_condition = execute_command(selected_command)

        json = {
                    "user_id": config["user_id"],
                    "command": selected_command,
                    "exit_condition": exit_condition,
                    "interaction_id": interaction_id,
                }
        if "model" in config:
            json["model"] = config["model"]
            print("Only the following LLM models are used by Gorilla: ", config["model"])
        
        # Commands failed / succeeded?
        try:
            response = requests.post(
                f"{SERVER_URL}/command-execution-result",
                json=json,
                timeout=30,
            )
            if response.status_code != 200:
                print("Failed to send command execution result to the server.")
        except requests.exceptions.Timeout:
            print("Failed to send command execution result to the server: Timeout.")


if __name__ == "__main__":
    main()
