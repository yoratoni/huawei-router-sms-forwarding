from pyostra import pyprint, LogTypes
from copy import deepcopy

import json
import os


class AppHistory:
    HISTORY_PATH = os.path.join(__file__, os.pardir, os.pardir, "history.json")
    HISTORY = {}

    
    @staticmethod
    def add_to_history(sms: dict, contacts: dict) -> dict:
        """Add a unique SMS (dict formatted) into the history
        and returns the SMS dict if needed (deep-copied).

        Args:
            sms (dict): Original unique SMS dict.
        """
    
        # Ensure that it does not modify the original SMS dict
        sep_sms = deepcopy(sms)
    
        # General validity
        if sep_sms is not None and "Index" in sep_sms:
            sms_id = sep_sms["Index"]
            sms_sender = sep_sms["Phone"]
                        
            # Parsing the dict to remove useless info
            try:
                # Add the contact name
                if sms_sender in contacts.keys():
                    sep_sms["ContactName"] = contacts[sms_sender]
                else:
                    sep_sms["ContactName"] = "NONE"
                
                # Useless info for the history
                sep_sms.pop("Smstat")
                sep_sms.pop("Index")
                sep_sms.pop("Sca")
                sep_sms.pop("SaveType")
                sep_sms.pop("Priority")
                sep_sms.pop("SmsType")
            except KeyError as err:
                pyprint(LogTypes.ERROR, f"SMS could not be parsed [{err}]", True)
            
            # Add to the history general dict
            AppHistory.HISTORY[sms_id] = sep_sms
            
        return deepcopy(AppHistory.HISTORY)

    
    @staticmethod
    def save_history() -> bool:
        """Saves the history dict into a json file.
        
        Note:
            Also creates the JSON "history" file if not found.
            
        Returns:
            bool: True if the history has been correctly saved.
        """
        
        # Detects file creation (prevents empty history dict catching)
        file_exists = os.path.exists(AppHistory.HISTORY_PATH)

        with open(AppHistory.HISTORY_PATH, "w+") as history_file:
            if isinstance(AppHistory.HISTORY, dict):
                # Empty history dict catch
                if len(AppHistory.HISTORY) == 0:
                    if file_exists:
                        return False
                    else:
                        # Empty dicts are not really supported by json.dump()
                        # And json.load() returns an error if the file is empty
                        # So a sample line is added
                        AppHistory.HISTORY["-1"] = "-1"
                
                json.dump(AppHistory.HISTORY, history_file, indent=4)
                return True

        return False
    

    @staticmethod
    def load_history() -> bool:
        """Loads the history from the json file
        into the AppHistory.HISTORY var (as a dict with SMS IDs).
        
        Note:
            It also detects if the path exists and creates an empty file if not.
            
        Returns:
            bool: True if the history has been correctly loaded.
        """
        
        # Creates the file if not initialized
        if not os.path.exists(AppHistory.HISTORY_PATH):
            AppHistory.save_history()
            pyprint(LogTypes.INFO, f"History file created")
            return False

        with open(AppHistory.HISTORY_PATH, "r") as history_file:
            try:
                AppHistory.HISTORY = json.load(history_file)
                
                # Removes the sample line
                if "-1" in AppHistory.HISTORY:
                    AppHistory.HISTORY.pop("-1")
                
                return True
            except json.JSONDecodeError as err:
                pyprint(LogTypes.ERROR, f"History file could not be loaded [{err}]", True)

        return False
