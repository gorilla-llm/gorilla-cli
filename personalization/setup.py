import os
import json
from openai import OpenAI
CONFIG_FILE = os.path.expanduser("~/.gorilla-cli-config.json")


class PersonalizationSetup:

    """
    Sets up the personalization options for the user.
    """

    def __init__(self):
        """
        Initially sets the personalization to Falsy values
        After, looks through the config/user files to populate relevant information

        On top of simply updating personalization settings, since we need to handle the old implementation of user IDs,
        we need to add the user-ID from the user-ID file.
        """
        self.personalization = False
        self.open_ai_key = None

        with open(CONFIG_FILE, "r") as config_file:
            self.config_json = json.load(config_file)
            print(self.config_json)
            if "personalization" not in self.config_json:
                self.config_json["personalization"] = {
                    "permission": False, "api_key": None}
                self.request_personalization()
            else:
                self.open_ai_key = self.config_json["personalization"]["api_key"]
                self.permission = self.config_json["personalization"]["permission"]

    def populatePersonalizationSettings(self):
        """
        Populates the json file with the relevant details/information
        """
        self.config_json["personalization"]["permission"] = self.personalization
        self.config_json["personalization"]["api_key"] = self.open_ai_key
        with open(CONFIG_FILE, "w") as config_file:
            json.dump(self.config_json, config_file)

    def checkOpenAIAPIValidity(self):
        """
        Checks if the provided OpenAI key is valid or not.
        """
        try:
            print (self.open_ai_key)
            client = OpenAI(api_key=self.open_ai_key)
            client.models.list()
            print ()
        except Exception as e:
            return False
        return True

    def changeOpenAIKey(self):
        """
        Enables the user to add an OpenAI key
        """
        self.open_ai_key = str(
            input("Enter your new OpenAI API key: ")).strip()
        while not self.checkOpenAIAPIValidity():
            response = str(input(
                "The API key you entered is invalid. Do you want to try again? [Y/n]: ")).strip().lower()
            if response in ["n", "no"]:
                self.open_ai_key = None
                return False
            else:
                self.open_ai_key = str(
                    input("Enter your new OpenAI API key: ")).strip()
        return True

    def editPersonalizationSettings(self, permission: bool):
        """
        This function enables a user to edit their personalization settings.

        We cover the following cases when the user wants to edit their settings:

        1. The user wants to personalize, but they already have it enabled. 
        In this case, we ask them if they want to change their API key or not.

        2. The user doesn't want to personalize, and they already have it disabled.
        We let them know that they already have it disabled.

        3. The user wants to personalize and they have it disabled. In that case, 
        we ask them to provide an API key.

        4. The user doesn't want to personalize, and they have it enabled. In that case,
        we turn off personalization for them.
        """

        if self.config_json["personalization"]["permission"] and permission:
            res = input(f"You are already using the the following API key:\n\n{self.open_ai_key}\n\nDo you want to change it?").strip().lower()
            if res in ["n", "no"]:
                print("You're all set.")
            else:
                old_key = self.open_ai_key
                success = self.changeOpenAIKey()
                if success:
                    print("We successfully updated your API key.")
                    self.personalization = True
                else:
                    print(
                        "You didn't provide a valid API key, so we didn't update your settings.")
                    self.personalization = True
                    self.open_ai_key = old_key

        # the user already has personalization not enabled so we kep it that way
        elif not self.config_json["personalization"]["permission"] and not permission:
            print("You already have personalization disabled. You're good to go!")
        # the case of turning personalization off
        elif self.config_json["personalization"]["permission"] and not permission:
            print("We turned off personalization for you.")
            self.personalization = False
            self.open_ai_key = None
        # the case of turning personalization on
        else:
            api_key = self.changeOpenAIKey()
            if api_key:
                print("We successfully added your API key.")
                self.personalization = True
            else:
                print(
                    "You didn't provide a valid API key, so we didn't update your settings.")
                self.personalization = False
                self.open_ai_key = None

        self.populatePersonalizationSettings()

    def request_personalization(self):
        """ 
        Ask the user if they want to personalize their bash history - depending on the Y/n response, set the personalize flag to true/false
        """
        response = input(
            "Do you want to personalize your bash history? [Y/n]: ").strip().lower()
        if response in ["n", "no"]:
            print("We won't use your bash history to personalize your queries. You can always turn this feature on in the future!")
            self.editPersonalizationSettings(False)
        else:
            print("We're going to be using your bash history to personalize your queries. This feature will require OpenAI API access, so enter your API key when prompted below. You can always turn this feature off in the future!")
            self.editPersonalizationSettings(True)
