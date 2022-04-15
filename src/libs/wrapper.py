from pyostra import pyprint, LogTypes
from dotenv import load_dotenv

import sys
import os


class HuaweiWrapper:
    ENV_DICT = {}
    
    @staticmethod
    def string_list_to_list(input: str) -> list:
        """Converts a string representation of a list
        coming from an .env file to a real Python list.
        
        Note:
            If the string representation of the list is invalid, returns an empty list.

        Args:
            input (str): The default string list.

        Returns:
            list: A python list.
        """
        
        output = []
        
        if "[" in input and "]" in input:
            output = input.strip("][").split(", ")
            
        for i, elem in enumerate(output):
            single = (elem[0] == "'" and elem[-1] == "'")
            double = (elem[0] == '"' and elem[-1] == '"')
            
            if single or double:
                output[i] = elem[1:-1]

        return output
        
    
    @staticmethod
    def get_formatted_env() -> dict:
        """Returns a dict containing the parsed .env file
        with all the data used for the Huawei API.

        Keys:
            - CONNECTION: Formatted URI for the API connection.
            - ROUTER_PHONE_NUMBER: International number of the router.
            - RECEIVER_PHONE_NUMBER: International number of the receiver (used for SMS rerouting).

        Returns:
            dict: Parsed dict.
        """
        
        # Loads the .env file and add as environment variables
        env_path = os.path.join(os.getcwd(), "src", ".env")
        load_dotenv(env_path)
        
        # Get internal env vars
        internal_dict = {
            "ROUTER_PHONE_NUMBER": None,
            "RECEIVER_PHONE_NUMBER": None,
            "ROUTER_IP_ADDRESS": None,
            "ACCOUNT_USERNAME": None,
            "ACCOUNT_PASSWORD": None,
            "LOOP_DELAY": None,
            "SMS_FILTER_SENDERS": None
        }

        for key in internal_dict.keys():
            value = os.getenv(key)
            
            if value is None:
                pyprint(LogTypes.CRITICAL, f"{key}: Missing input, please verify the .env file.")
                sys.exit(1)
                
            internal_dict[key] = value
            
        # Dict containing formatted outputs used for the Huawei API
        res_dict = {}
        
        # Formatted connection URI
        res_dict["CONNECTION"] = "http://{0}:{1}@{2}".format(
            internal_dict["ACCOUNT_USERNAME"],
            internal_dict["ACCOUNT_PASSWORD"],
            internal_dict["ROUTER_IP_ADDRESS"]
        )
        
        # Phone numbers
        res_dict["ROUTER_PHONE_NUMBER"] = internal_dict["ROUTER_PHONE_NUMBER"].replace(" ", "")
        res_dict["RECEIVER_PHONE_NUMBER"] = internal_dict["RECEIVER_PHONE_NUMBER"].replace(" ", "")
        
        # Delay used for the loop
        res_dict["LOOP_DELAY"] = int(internal_dict["LOOP_DELAY"])
        
        # Filter
        res_dict["SMS_FILTER_SENDERS"] = internal_dict["SMS_FILTER_SENDERS"]

        return res_dict
    