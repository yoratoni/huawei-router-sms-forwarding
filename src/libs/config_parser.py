from libs.logger import pyprint, LogTypes
from typing import Union

import yaml
import sys
import os


class ConfigParser:
    """
    Loads the config.yaml file and format it, allowing it to be used by the app.
    """

    @staticmethod
    def load_yaml(devConfig: bool = False):
        """
        Loads the .yaml file and returns it as a dict.

        Args:
            devConfig (bool, optional): If True, the function will load the config.dev.yaml file (defaults to False).

        Returns:
            dict: Parsed dict containing the .yaml file config.
        """

        if devConfig:
            filename = "config.dev.yaml"
        else:
            filename = "config.yaml"

        # Path to the .yaml file (app.py main file to get the path)
        yaml_path = os.path.join(os.path.dirname(sys.argv[0]), filename)

        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as yaml_file:
                return yaml.safe_load(yaml_file)
        else:
            pyprint(LogTypes.CRITICAL, "The config.yaml file cannot be found, please, check that you renamed the file 'example.yaml' to 'config.yaml'", True)
            sys.exit(1)

    @staticmethod
    def format_phone_number(phone_number: str) -> str:
        """
        Formats a phone number to an international format without spaces.

        Note:
            - Supports empty strings.
            - This function acts as critical, so if the phone number is invalid
            the app will exit.

        Args:
            phone_number (str): The original phone number.

        Returns:
            str: The formatted & verified phone number.
        """

        # Support empty strings
        if phone_number == "":
            return ""

        # Remove spaces
        phone_number = phone_number.replace(" ", "")

        # Check if the first character is a +
        if phone_number[0] != "+":
            pyprint(LogTypes.CRITICAL, f"The phone number must start with a + [{phone_number}]", True)
            sys.exit(1)

        # Check if the phone number is valid
        if not phone_number[1:].isdigit():
            pyprint(LogTypes.CRITICAL, f"The phone number must contain only numbers [{phone_number}]", True)
            sys.exit(1)

        return phone_number

    @staticmethod
    def get_config(devConfig: bool = False) -> dict[str, Union[str, list[str], int, None, dict[str, str]]]:
        """
        Returns a dict containing the parsed .yaml file
        with all the data used by the app.

        Keys:
            - ROUTER_URI: Formatted URI for the API connection.
            - ROUTER_IP_ADDRESS: IP address of the router.
            - ROUTER_PHONE_NUMBER: International number of the router.
            - ROUTER_USERNAME: Username of the router (account).
            - ROUTER_PASSWORD: Password of the router (account).
            - ROUTER_LOOP_SLEEP: Delay between each loop iteration.
            - CONTACTS: Dict containing all the contacts.
            - FORWARDERS: Dict containing all the forwarders.
            - REPLIERS: Dict containing all the repliers.

        Args:
            devConfig (bool, optional): If True, the function will load the config.dev.yaml file (defaults to False).

        Returns:
            dict: Parsed dict containing all the .yaml file config.
        """

        res: dict[str, Union[str, list[str], int, None, dict[str, str]]] = {
            "ROUTER_URI": None,
            "ROUTER_IP_ADDRESS": None,
            "ROUTER_PHONE_NUMBER": None,
            "ROUTER_USERNAME": None,
            "ROUTER_PASSWORD": None,
            "ROUTER_LOOP_SLEEP": None,
            "CONTACTS": {},
            "FORWARDERS": {},
            "REPLIERS": {}
        }

        # Loads the .yaml file
        yaml_dict = ConfigParser.load_yaml(devConfig)

        # Get router data
        res["ROUTER_IP_ADDRESS"] = yaml_dict["router"]["ip_address"]
        res["ROUTER_PHONE_NUMBER"] = ConfigParser.format_phone_number(yaml_dict["router"]["phone_number"])
        res["ROUTER_USERNAME"] = yaml_dict["router"]["username"]
        res["ROUTER_PASSWORD"] = yaml_dict["router"]["password"]
        res["ROUTER_LOOP_SLEEP"] = yaml_dict["router"]["loop"]

        res["ROUTER_URI"] = "http://{0}:{1}@{2}".format(
            res["ROUTER_USERNAME"],
            res["ROUTER_PASSWORD"],
            res["ROUTER_IP_ADDRESS"]
        )

        # Get contacts data
        if "contacts" in yaml_dict:
            temp_contacts = yaml_dict["contacts"]

            for contact in temp_contacts:
                if "phone_number" in contact and "name" in contact:
                    formatted_phone_number = ConfigParser.format_phone_number(contact["phone_number"])

                    # Ignores the empty placeholders
                    if formatted_phone_number != "":
                        if contact["name"] == "":
                            pyprint(LogTypes.CRITICAL, f"Empty name for contact: {contact}", True)
                            sys.exit(1)

                        res["CONTACTS"][formatted_phone_number] = contact["name"] # type: ignore
                else:
                    pyprint(LogTypes.WARN, f"Invalid contact: {contact}", True)

        # Get forwarders data
        if "forwarders" in yaml_dict:
            temp_forwarders = yaml_dict["forwarders"]

            for forwarder in temp_forwarders:
                if "phone_number" in forwarder and "whitelist" in forwarder:
                    formatted_phone_number = ConfigParser.format_phone_number(forwarder["phone_number"])
                    formatted_whitelist = [
                        ConfigParser.format_phone_number(phone_number) for phone_number in forwarder["whitelist"]
                    ]

                    # Ignores the empty placeholders
                    if formatted_phone_number != "":
                        res["FORWARDERS"][formatted_phone_number] = formatted_whitelist # type: ignore
                else:
                    pyprint(LogTypes.WARN, f"Invalid forwarder: {forwarder}", True)

        # Get repliers data
        if "repliers" in yaml_dict:
            temp_repliers = yaml_dict["repliers"]

            for replier in temp_repliers:
                if "phone_number" in replier and "messages" in replier:
                    formatted_phone_number = ConfigParser.format_phone_number(replier["phone_number"])

                    # Ignores the empty placeholders
                    if formatted_phone_number != "":
                        res["REPLIERS"][formatted_phone_number] = replier["messages"] # type: ignore

        # Verify if the data is valid
        for key in res:
            if res[key] is None:
                pyprint(LogTypes.CRITICAL, f"Invalid config: {key} is None", True)
                sys.exit(1)

        return res