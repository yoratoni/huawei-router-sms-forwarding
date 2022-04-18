from pyostra import pyprint, LogTypes
from datetime import date, datetime
from dotenv import load_dotenv

import sys
import os


class AppUtils:
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
        
        if raw_input is not None and len(raw_input) > 0:
            # Be sure that there's no ending comma
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
        contacts_list = AppUtils.string_list_to_list(contacts)
        
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
        
        # Loads the .env file and add as environment variables
        env_path = os.path.join(os.getcwd(), "src", ".env")
        load_dotenv(env_path)
        
        # Get internal env vars
        internal_dict = {
            "ROUTER_IP_ADDRESS": None,
            "ACCOUNT_USERNAME": None,
            "ACCOUNT_PASSWORD": None,
            "ROUTER_PHONE_NUMBER": None,
            "USER_PHONE_NUMBER": None,
            "SENDERS_WHITELIST": None,
            "CONTACTS": None,
            "LOOP_DELAY": None,
            "DELETE_SYSTEM": None
        }

        for key in internal_dict.keys():
            value = os.getenv(key)
            
            if value is None:
                pyprint(LogTypes.CRITICAL, f"{key}: Missing input, please verify the .env file.")
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
        
        # Number of forwarded SMS before starting to delete the old ones
        system_dict["DELETE_SYSTEM"] = int(internal_dict["DELETE_SYSTEM"])
        
        # SMS senders whitelist
        system_dict["SENDERS_WHITELIST"] = AppUtils.string_list_to_list(internal_dict["SENDERS_WHITELIST"])
        
        # List of contacts that replaces the raw phone numbers.
        system_dict["CONTACTS"] = AppUtils.format_contacts(internal_dict["CONTACTS"])

        return system_dict    

    
    @staticmethod
    def format_date(sms_date: str) -> str:
        """Used to format the date inside the forwarded SMS.

        Args:
            sms_date (str): The original string date coming from the SMS dict.

        Returns:
            str: Formatted date depending on the day.
        """
        
        sms_datetime = datetime.strptime(sms_date, "%Y-%m-%d %H:%M:%S")
  
        # Same day -> Only time
        if sms_datetime.day == datetime.today().day:
            return sms_datetime.strftime("%H:%M:%S")

        return sms_date
