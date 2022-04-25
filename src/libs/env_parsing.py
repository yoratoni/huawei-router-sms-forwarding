from pyostra import pyprint, LogTypes
from dotenv import load_dotenv

import textwrap
import sys
import os


class EnvParsing:
    DEFAULT_ENV = textwrap.dedent("""\
    # Your router IP address (generally 192.168.8.1)
    ROUTER_IP_ADDRESS=192.168.8.1

    # Account details (the same one used to identify yourself on the local Huawei router website)
    ACCOUNT_USERNAME=""
    ACCOUNT_PASSWORD=""

    # International phone numbers of the router and the user, example: "+33 5 42 56 48 21"
    # Spaces are removed when the file is loaded so you can add spaces if you want
    # User phone number is the number where all the forwarded SMS are going
    ROUTER_PHONE_NUMBER=""
    USER_PHONE_NUMBER=""

    # Senders whitelist
    # Example: ["+33937023216"] means that only SMS sent by this number are forwarded
    # Leaving the list empty deactivates this option
    # Spaces and uppercase characters can be used
    SENDERS_WHITELIST=[]

    # Allows you to replace phone numbers by contact names inside the forwarded SMS
    # Formatted as a list where a phone number is followed by its contact name
    # Example: ["+33123456789", "Binance"] -> This number will be replaced by "Binance"
    CONTACTS=[]

    # Delay used to check SMS in a loop (in seconds)
    LOOP_DELAY=15
    """
    )
    
    
    @staticmethod
    def string_list_to_list(raw_input: str) -> list:
        """Converts a string representation of a list
        coming from an .env file to a real Python list.
        
        Note:
            If the string representation of the list is invalid, returns an empty list.

        Args:
            raw_input (str): The default string list.

        Returns:
            list: A python list.
        """
        
        output = []
        
        if raw_input is not None and len(raw_input) > 0 and raw_input != "[]":
            # Remove ending comma
            if raw_input[-2] == ",":
                raw_input = raw_input[:-2] + "]"
            
            if "[" in raw_input and "]" in raw_input:
                output = raw_input.strip("][").split(", ")
                
            for i, elem in enumerate(output):
                single = (elem[0] == "'" and elem[-1] == "'")
                double = (elem[0] == '"' and elem[-1] == '"')
                
                if single or double:
                    output[i] = elem[1:-1]

        return output
    
    
    @staticmethod
    def format_contacts(contacts: str) -> dict:
        """Used to convert the contacts string represented list to a formatted dict,
        it uses string_list_to_list() then it formats it into a dict.
        
        Args:
            contacts (str): Original string represented list of contacts.

        Returns:
            dict: Formatted dict of contacts.
        """
        
        output = {}
        contacts_list = EnvParsing.string_list_to_list(contacts)
        
        if contacts_list is not None:
            driver = len(contacts_list)
        
            if driver > 0:
                for i in range(0, driver, 2):
                    if i + 1 < driver:
                        output[contacts_list[i]] = contacts_list[i+1]
                    else:
                        output[contacts_list[i]] = "MISSING_NAME"
        
        return output
    
    
    @staticmethod
    def load_env():
        """Loads the .env file into the environment variables,
        with file creation if not found and exception catching.
        """
        
        # Relative path to the file
        env_path = os.path.join(__file__, os.pardir, os.pardir, ".env")
        
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            try:
                with open(env_path, "w+") as env_file:
                    env_file.write(EnvParsing.DEFAULT_ENV)
            except Exception as err:
                pyprint(LogTypes.CRITICAL, f"The .env file cannot be created [{err}]", True)
                sys.exit(1)
                

    @staticmethod
    def get_formatted_env() -> dict:
        """Returns a dict containing the parsed .env file
        with all the data used by the app.

        Keys:
            - URI: Formatted URI for the API connection.
            - ROUTER_PHONE_NUMBER: International number of the router.
            - USER_PHONE_NUMBER: International number of the user (used for SMS forwarding).
            - LOOP_DELAY: Time in seconds between two iterations of the main infinite loop.
            - SENDERS_WHITELIST: Whitelist containing available senders for forwarding.
            
        Returns:
            dict: Parsed dict containing all the .env file variables.
        """
        
        # Loads the .env file
        EnvParsing.load_env()
        
        # Get internal env vars
        internal_dict = {
            "ROUTER_IP_ADDRESS": None,
            "ACCOUNT_USERNAME": None,
            "ACCOUNT_PASSWORD": None,
            "ROUTER_PHONE_NUMBER": None,
            "USER_PHONE_NUMBER": None,
            "SENDERS_WHITELIST": None,
            "CONTACTS": None,
            "LOOP_DELAY": None
        }

        for key in internal_dict.keys():
            value = os.getenv(key)
            
            if value is None or len(value) == 0:
                pyprint(LogTypes.CRITICAL, f"'{key}': Missing input, please verify the .env file.", True)
                sys.exit(1)
                
            internal_dict[key] = value
            
        # Dict containing formatted outputs used for the Huawei API
        system_dict = {}
        
        # Formatted connection URI
        system_dict["URI"] = "http://{0}:{1}@{2}".format(
            internal_dict["ACCOUNT_USERNAME"],
            internal_dict["ACCOUNT_PASSWORD"],
            internal_dict["ROUTER_IP_ADDRESS"]
        )
        
        # Phone numbers
        system_dict["ROUTER_PHONE_NUMBER"] = internal_dict["ROUTER_PHONE_NUMBER"].replace(" ", "")
        system_dict["USER_PHONE_NUMBER"] = internal_dict["USER_PHONE_NUMBER"].replace(" ", "")
        
        # Delay used for the loop
        system_dict["LOOP_DELAY"] = int(internal_dict["LOOP_DELAY"])
        
        # SMS senders whitelist
        system_dict["SENDERS_WHITELIST"] = EnvParsing.string_list_to_list(internal_dict["SENDERS_WHITELIST"])
        
        # List of contacts that replaces the raw phone numbers.
        system_dict["CONTACTS"] = EnvParsing.format_contacts(internal_dict["CONTACTS"])

        return system_dict    
