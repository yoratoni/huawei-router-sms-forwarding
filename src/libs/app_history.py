from libs import logger
from typing import Optional
from copy import deepcopy

import json
import sys
import os


class AppHistory:
    HISTORY_PATH = os.path.join(os.path.dirname(sys.argv[0]), "logs/history.json")
    history: dict[str, dict[str, str]] = {}


    @staticmethod
    def add_to_history(sms: Optional[dict[str, str]]) -> None:
        """
        Add a unique SMS (dict formatted) into the history
        and returns the SMS dict if needed (deep-copied).

        Args:
            sms (dict, optional): Original unique SMS dict.
        """

        # Ensure that it does not modify the original SMS dict
        sep_sms = deepcopy(sms)

        # General validity
        if sep_sms is not None and "Index" in sep_sms:
            sms_id = sep_sms["Index"]

            # Parsing the dict to remove useless info
            try:
                # Add the contact name
                if "Contact" in sep_sms:
                    sep_sms["Contact"] = sep_sms["Contact"]

                # Useless info for the history
                sep_sms.pop("Smstat")
                sep_sms.pop("Index")
                sep_sms.pop("Sca")
                sep_sms.pop("SaveType")
                sep_sms.pop("Priority")
                sep_sms.pop("SmsType")
            except KeyError as err:
                logger.error(f"SMS could not be parsed:\n{err}")

            # Add to the history general dict
            AppHistory.history[sms_id] = sep_sms


    @staticmethod
    def save_history() -> bool:
        """
        Saves the history dict into a json file.

        Note:
            Also creates the JSON "history" file if not found.

        Returns:
            bool: True if the history has been correctly saved.
        """

        # Directory creation
        if not os.path.exists(os.path.dirname(AppHistory.HISTORY_PATH)):
            try:
                os.makedirs(os.path.dirname(AppHistory.HISTORY_PATH))
            except OSError as err:
                logger.error(f"History directory could not be created:\n{err}")

        # Detects file creation (prevents empty history dict catching)
        file_exists = os.path.exists(AppHistory.HISTORY_PATH)

        try:
            with open(AppHistory.HISTORY_PATH, "w+") as history_file:
                # Empty history dict catch
                if len(AppHistory.history) == 0:
                    if file_exists:
                        return False

                json.dump(AppHistory.history, history_file, indent=4)

                return True
        except FileNotFoundError as err:
            logger.warning(f"History file could not be found:\n{err}")
        except PermissionError as err:
            logger.warning(f"History file could not be written:\n{err}")

        return False


    @staticmethod
    def load_history() -> bool:
        """
        Loads the history from the json file
        into the AppHistory.history var (as a dict with SMS IDs).

        Note:
            It also detects if the path exists and creates an empty file if not.

        Returns:
            bool: True if the history has been correctly loaded.
        """

        # Creates the file if not initialized
        if not os.path.exists(AppHistory.HISTORY_PATH):
            history_state = AppHistory.save_history()
            return history_state

        try:
            with open(AppHistory.HISTORY_PATH, "r") as history_file:
                try:
                    AppHistory.history = json.load(history_file)

                    return True
                except json.JSONDecodeError as err:
                    # Empty files support (json.load() returns an error)
                    AppHistory.history = {}

                    return True
        except FileNotFoundError as err:
            logger.warning(f"History file could not be found:\n{err}")
        except PermissionError as err:
            logger.warning(f"History file could not be read:\n{err}")
        except Exception as err:
            logger.error(f"History file could not be loaded:\n{err}")

        return False
