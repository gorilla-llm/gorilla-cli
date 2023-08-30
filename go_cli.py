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
import urllib.parse
import sys
from halo import Halo
import go_questionary

__version__ = "0.0.10"  # current version
SERVER_URL = "https://cli.gorilla-llm.com"
UPDATE_CHECK_FILE = os.path.expanduser("~/.gorilla-cli-last-update-check")
USERID_FILE = os.path.expanduser("~/.gorilla-cli-userid")
ISSUE_URL = f"https://github.com/gorilla-llm/gorilla-cli/issues/new"
GORILLA_EMOJI = "🦍 " if go_questionary.try_encode_gorilla() else ""
WELCOME_TEXT = f"""{GORILLA_EMOJI}Welcome to Gorilla-CLI! Enhance your Command Line with the power of LLMs! 

Simply use `gorilla <your desired operation>` and Gorilla will do the rest. For instance:
    gorilla generate 100 random characters into a file called test.txt
    gorilla get the image ids of all pods running in all namespaces in kubernetes
    gorilla list all my GCP instances

A research prototype from UC Berkeley, Gorilla-CLI ensures user control and privacy:
 - Commands are executed only with explicit user approval.
 - While queries and error (stderr) logs are used to refine our model, we NEVER gather output (stdout) data.

Visit github.com/gorilla-llm/gorilla-cli for examples and to learn more!"""


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
            issue_title = urllib.parse.quote(
                f"Problem with generating userid: {str(e)}"
            )
            issue_body = urllib.parse.quote(f"Unable to generate userid: {str(e)}")
            print("Unable to generate userid:", e)
            print(
                f"Please run 'go <command>' again. If the problem persists, please raise an issue: \
                  {ISSUE_URL}?title={issue_title}&body={issue_body}"
            )
        try:
            with open(USERID_FILE, "w") as f:
                f.write(user_id)
            return user_id
        except Exception as e:
            issue_title = urllib.parse.quote("Problem with userid file")
            issue_body = urllib.parse.quote(f"Unable to write userid file: {str(e)}")
            print("Unable to write userid file:", e)
            print(
                f"Try deleting USERID_FILE and run 'go <command>' again. If the problem persists, please raise an issue:\
                   {ISSUE_URL}?title={issue_title}&body={issue_body}"
            )


def main():
    def execute_command(cmd):
        process = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)
        error_msg = process.stderr.decode("utf-8", "ignore")
        if error_msg:
            print(f"{error_msg}")
            return error_msg
        return str(process.returncode)

    args = sys.argv[1:]
    user_input = " ".join(args)
    user_id = get_user_id()

    # Generate a unique interaction ID
    interaction_id = str(uuid.uuid4())

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
            "", choices=commands, instruction=""
        ).ask()
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
