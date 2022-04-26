from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api import exceptions as HuaweiExceptions
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.Client import Client

from pyostra import pyprint, LogTypes
from libs import AppHistory
from datetime import datetime
from typing import Union

import textwrap
import time
import sys


class HuaweiWrapper:
    # Used to avoid sending the same SMS multiple times
    # In the case of a SMS received/sended at the exact same time as a new iteration
    LAST_RECEIVED_SMS_ID = ""
    LAST_SENDED_SMS_ID = ""
    
    
    @staticmethod
    def connect_to_api(uri: str) -> Union[Client, None]:
        """Connect to the API and returns the client object (with full exception handling).

        Args:
            uri (str): URI generated from HuaweiWrapper.get_formatted_env() ("URI" key).

        Returns:
            Union[Client, None]: The client object used to interact with the API
                or None if it can't connect to the API.
        """
        
        log_state = None
        log_msg = None
        client = None
 
        try:
            client = Client(AuthorizedConnection(uri))
            log_state = LogTypes.INFO
            log_msg = "Successfully connected to the router"
                
        except HuaweiExceptions.ResponseErrorLoginRequiredException:
            log_state = LogTypes.WARN
            log_msg = "Expired session, login again in the next loop"
        
        except HuaweiExceptions.LoginErrorAlreadyLoginException:
            log_state = LogTypes.WARN
            log_msg = textwrap.dedent(f"""\
                Client is already logged in but a new attempt has been made,
                wait until the Huawei router automatically disconnect old clients.
                """)
            
        except Exception as err:
            log_state = LogTypes.CRITICAL
            log_msg = f"Router connection failed! Please check the .env settings [{err}]"

        # Main log
        pyprint(log_state, log_msg, True)
    
        # Critical exception catch
        if log_state == LogTypes.CRITICAL:
            sys.exit(1)
        
        return client
    
    
    @staticmethod
    def api_connection_loop(client: Union[Client, None], uri: str) -> Client:
        """Try to connect to the API using a loop and a time sleeping system.

        Args:
            client (Union[Client, None]): To test if the client is already connected.
            uri (str): URI generated from HuaweiWrapper.get_formatted_env() ("URI" key).

        Returns:
            Client: The updated client.
        """

        # Infinite loop limit
        inf_loop_limit = 12
        iteration = 0
        
        while client is None:
            pyprint(LogTypes.INFO, "Trying to connect to the router..")
            client = HuaweiWrapper.connect_to_api(uri)
            
            if iteration > inf_loop_limit:
                error_msg = textwrap.dedent(f"""\
                Could not connect to the router after {iteration} attempts.

                Debugging:
                - Verify the settings inside the .env file and if your Huawei router is online.
                - Verify that your router is compatible, here's the list of compatible models:
                    Huawei B310s-22
                    Huawei B315s-22
                    Huawei B525s-23a
                    Huawei B525s-65a
                    Huawei B715s-23c
                    Huawei B528s
                    Huawei B535-232
                    Huawei B628-265
                    Huawei B818-263
                    Huawei E5186s-22a
                    Huawei E5576-320
                    Huawei E5577Cs-321
                """)
                
                pyprint(LogTypes.CRITICAL, error_msg, True)
                sys.exit(1)
            
            iteration += 1
            
            # New attempt every 5 seconds
            if client is None:
                time.sleep(5)
            
        return client
        

    @staticmethod
    def disconnect(client: Union[Client, None]):
        """Try-except disconnection from the Huawei Router.

        Args:
            client (Union[Client, None]): To test if the client is already connected.
        """
        
        try:
            # If client instance exists, disconnect from the router
            if client is not None:
                client.user.logout()
                AppHistory.save_history()
                pyprint(LogTypes.INFO, "Successfully disconnected from the router")
        except Exception:
            pass
        
        sys.exit(1)
        

    @staticmethod
    def unique_sms_id_check(sms: dict) -> bool:
        """Used to avoid sending the same SMS multiple times
        in the case of a SMS received at the exact same time as a new iteration.

        Note:
            Saves the last SMS ID and verify that it is not already sent.

        Args:
            sms (dict): The last received SMS dict.

        Returns:
            bool: True if the SMS can be sent.
        """
        
        if sms is not None and "Index" in sms.keys():
            ID = sms["Index"]
            
            if ID != HuaweiWrapper.LAST_RECEIVED_SMS_ID:
                HuaweiWrapper.LAST_RECEIVED_SMS_ID = ID
                return True
            else:
                return False
        

    @staticmethod
    def is_sms_whitelisted(sms_sender: str, senders_whitelist: list[str]) -> bool:
        """Returns True if the SMS is sent by one of the senders
        listed inside the .env file ("SENDERS_WHITELIST" list).
        
        Note:
            If the whitelist system is deactivated, it returns True.

        Args:
            sms_sender (str): The SMS sender (unique SMS dict -> "Phone" key).
            senders_whitelist (list): Coming from the formatted env dict ("SENDERS_WHITELIST" key).

        Returns:
            bool: True if the SMS is sent by one of the senders listed.
        """
        
        if senders_whitelist is not None and len(senders_whitelist) > 0:      
            # Formatted using replace() & lower() to match senders        
            sms_sender = sms_sender.replace(" ", "").lower()

            for included_sender in senders_whitelist:
                if sms_sender == included_sender.replace(" ", "").lower():
                    return True
                
            return False
        else:
            return True
        

    @staticmethod
    def get_last_sms(client: Client, senders_whitelist: list[str], ignore_read: bool = True) -> Union[dict, None]:
        """Returns the last sms received by the router,
        including senders whitelist and unread priority.

        Args:
            client (Client): _description_
            senders_whitelist (list[str]): List of all the whitelisted SMS senders.
            ignore_read (bool, optional): If True, ignores already read SMS.

        Returns:
            Union[dict, None]: A dict containing all the SMS info,
                None if no SMS found or if the SMS is already read and "ignore_read" is set to True.
        """
        
        try:
            # Get last received SMS (Unread priority)
            sms_list = client.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 1, 0, 0, 1)
            sms_read_state = int(sms_list["Messages"]["Message"]["Smstat"])
            sms = sms_list["Messages"]["Message"]
            
            # SMS already read
            if ignore_read and sms_read_state == 1:
                sms = None

            # Verify that the last sent SMS have not the same ID
            sms_uniqueness = HuaweiWrapper.unique_sms_id_check(sms)
            
            if sms_uniqueness and sms is not None:
                # Get useful SMS data
                sms_date = sms["Date"]
                sms_sender = sms["Phone"]
                
                # Whitelist system (If the whitelist is deactivated, all new SMS are whitelisted)
                is_whitelisted = HuaweiWrapper.is_sms_whitelisted(sms_sender, senders_whitelist)

                if is_whitelisted:
                    # Set the SMS status to read
                    client.sms.set_read(int(sms["Index"]))
                    
                    # Main Log
                    pyprint(LogTypes.DATA, f"({sms_date}) New SMS received from {sms_sender}")
            else:
                pyprint(LogTypes.INFO, "No new SMS found..")
                
        except Exception as err:
            pyprint(LogTypes.ERROR, f"Last SMS received by the router cannot be returned [{err}]", True)
            sms = None
        
        return sms


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


    @staticmethod
    def format_sms(sms: dict, contacts: dict) -> str:
        """Use the SMS dict info to format a messages used for the forwarding.

        Args:
            sms (dict): Original SMS dict.
            contacts (dict): Dict of available contacts that replaces the raw phone numbers.

        Returns:
            str: Formatted string of the message.
        """
        
        # Get SMS info    
        sms_date = HuaweiWrapper.format_date(sms["Date"])
        sms_sender = sms["Phone"]
        sms_content = sms["Content"]
    
        # Replaces the number by a contact name
        if sms_sender in contacts.keys():
            sms_sender = contacts[sms_sender]
    
        # Formatted string
        formatted_sms = f"[{sms_date}] New SMS from {sms_sender}:\n\n{sms_content}"
        
        return formatted_sms


    @staticmethod
    def send_sms(client: Client, sms_content: str, phone_number: str) -> bool:
        """Allows to send an SMS to a number (international formatted such as "+33937023216").

        Args:
            client (Client): Returned from HuaweiWrapper.api_connection_loop().
            sms_content (str): Content of the original SMS dictionnary.
            phone_number (str): String formatted phone number (example: "+33937023216").

        Returns:
            bool: True if the SMS has been correctly sent to the user.
        """
        
        gen_state = False
        error_reason = ""
        
        try:
            # Sending SMS request
            sms_request = client.sms.send_sms([phone_number], sms_content)
            
            # huawei_lte_api SMS system returns "OK" instead of a boolean..
            if sms_request == "OK":
                gen_state = True
            else:
                gen_state = False
                error_reason = "Huawei LTE API returned an invalid response"
            
        except Exception as err:
            gen_state = False
            error_reason = err

        if not gen_state:
            pyprint(LogTypes.ERROR, f"SMS cannot be sent to {phone_number} [{error_reason}]", True)
        else:
            pyprint(LogTypes.SUCCESS, f"SMS correctly forwarded to {phone_number}", True)

        return gen_state
    

    @staticmethod
    def forward_sms(client: Client, sms: dict, contacts: dict, phone_number: str) -> bool:
        """Allows to forward a formatted SMS to another phone number,
        includes contacts & history systems.

        Args:
            client (Client): Returned from HuaweiWrapper.api_connection_loop().
            sms (dict): Original SMS dictionnary.
            contacts (dict): List of contacts that replaces the raw phone numbers (inside the .env file).
            phone_number (str): String formatted phone number (example: "+33937023216").

        Returns:
            bool: _description_
        """

        if sms is not None and "Index" in sms:
            # Avoid duplicata
            if sms["Index"] != HuaweiWrapper.LAST_SENDED_SMS_ID:
                sms_content = HuaweiWrapper.format_sms(sms, contacts)
                api_response = HuaweiWrapper.send_sms(client, sms_content, phone_number)
                
                if api_response:
                    AppHistory.add_to_history(sms, contacts)
                    return True
            else:
                pyprint(LogTypes.WARN, "This SMS seems to have been already sended once")
            
        return False
