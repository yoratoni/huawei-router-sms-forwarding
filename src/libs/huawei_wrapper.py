from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api import exceptions as HuaweiExceptions
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.Client import Client

from pyostra import pyprint, LogTypes
from dotenv import load_dotenv
from libs import AppUtils
from typing import Union

import sys
import os


class HuaweiWrapper:
    # Connection state of the client:
    #   "-1": Not yet connected (Unique first-time marker state)
    #    "0": Client is successfully connected
    #    "1": Expired session, client needs to login again
    #    "2": Client is already logged in but a new attempt has been made
    CLIENT_CONNECTION_STATE = 0
    
    # Object of the client (huawei_lte_api.Client -> Client)
    CLIENT_OBJ = None
    
    
    @staticmethod
    def get_formatted_env() -> dict:
        """Returns a dict containing the parsed .env file
        with all the data used for the Huawei API.

        Keys:
            - URI: Formatted URI for the API connection.
            - ROUTER_PHONE_NUMBER: International number of the router.
            - RECEIVER_PHONE_NUMBER: International number of the receiver (used for SMS rerouting).
            - LOOP_DELAY: Time in seconds between two iterations of the main infinite loop.
            - SMS_FILTER: Filter the SMS by senders, example: ["Binance"] means only SMS coming from Binance.
            
        Returns:
            dict: Parsed dict.
        """
        
        # Loads the .env file and add as environment variables
        env_path = os.path.join(os.getcwd(), "src", ".env")
        load_dotenv(env_path)
        
        # Get internal env vars
        internal_dict = {
            "ROUTER_IP_ADDRESS": None,
            "LOOP_DELAY": None,
            "ACCOUNT_USERNAME": None,
            "ACCOUNT_PASSWORD": None,
            "ROUTER_PHONE_NUMBER": None,
            "RECEIVER_PHONE_NUMBER": None,
            "SMS_FILTER": None,
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
        res_dict["URI"] = "http://{0}:{1}@{2}".format(
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
        res_dict["SMS_FILTER"] = AppUtils.string_list_to_list(internal_dict["SMS_FILTER"])

        return res_dict


    @staticmethod
    def set_connection_state(connection_state: int):
        """Set the current connection state of the client.

        Connection state of the client:
          "-1": Not yet connected (Unique first-time marker state)
           "0": Client is successfully connected
           "1": Expired session, client needs to login again
           "2": Client is already logged in but a new attempt has been made
        """
        
        HuaweiWrapper.CLIENT_CONNECTION_STATE = connection_state


    @staticmethod
    def get_connection_state() -> int:
        """Returns the current connection state of the client.

        Connection state of the client:
          "-1": Not yet connected (Unique first-time marker state).
           "0": Client is successfully connected.
           "1": Expired session, client needs to login again.
           "2": Client is already logged in but a new attempt has been made.

        Returns:
            int: Client connection state.
        """
        
        return HuaweiWrapper.CLIENT_CONNECTION_STATE


    @staticmethod
    def connect_to_api(uri: str) -> Client:
        """Connect to the API and returns the client object (with full exception handling).

        Args:
            uri (str): URI generated from HuaweiWrapper.get_formatted_env() ("URI" key).

        Returns:
            Client: The client object used to interact with the API.
        """
        
        state = HuaweiWrapper.get_connection_state()

        try:
            HuaweiWrapper.CLIENT_OBJ = Client(AuthorizedConnection(uri))
            pyprint(LogTypes.INFO, "Successfully connected to the router", True)
            state = 0
                
        except HuaweiExceptions.ResponseErrorLoginRequiredException:
            pyprint(LogTypes.WARN, "Expired session, login again in the next loop", True)
            state = 1
        
        except HuaweiExceptions.LoginErrorAlreadyLoginException:
            pyprint(LogTypes.WARN, "Client is already logged in but a new attempt has been made", True)
            state = 2

        except Exception as err:
            pyprint(LogTypes.CRITICAL, f"Router connection failed! Please check the .env settings\n{err}", True)
            sys.exit(1)

        if state is not None:
            HuaweiWrapper.set_connection_state(state)
        else:
            HuaweiWrapper.set_connection_state(1)

        return HuaweiWrapper.CLIENT_OBJ


    @staticmethod
    def get_last_sms(client: Client, ignore_read: bool = True) -> Union[dict, None]:
        """Returns the last sms received by the router.

        Args:
            client (Client): _description_
            ignore_read (bool, optional): If True, ignores already read SMS.

        Returns:
            Union[dict, None]: A dict containing all the SMS info,
                None if no SMS found or if the SMS is already read and "ignore_read" is set to True.
        """
        
        # Get last received SMS (Unread priority)
        sms = client.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 1, 0, 0, 1)
        sms_read_state = int(sms["Messages"]["Message"]["Smstat"])
        sms_content = sms["Messages"]
        
        # No SMS found
        if sms_content is None:
            return None
        
        # SMS already read
        if sms_read_state == 1 and ignore_read:
            return None

        # Get useful SMS data
        sms_date = sms_content["Message"]["Date"]
        sms_sender = sms_content['Message']['Phone']
        
        # Main log
        pyprint(LogTypes.DATA, f"({sms_date}) New SMS received from {sms_sender}")
        
        return sms_content
