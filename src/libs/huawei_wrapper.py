from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api import exceptions as HuaweiExceptions
from huawei_lte_api.enums.sms import BoxTypeEnum, SortTypeEnum
from huawei_lte_api.Client import Client

from libs import logger
from libs.config_parser import ConfigParser
from libs.app_history import AppHistory
from datetime import datetime
from typing import Optional

import textwrap
import time
import sys


class HuaweiWrapper:
    # Used to avoid sending the same SMS multiple times
    # In the case of a SMS received/sent at the exact same time as a new iteration
    last_received_sms_id = ""
    last_sent_sms_id = ""


    @staticmethod
    def connect_to_api(uri: str) -> Optional[Client]:
        """
        Connect to the API and returns the client object (with full exception handling).

        Args:
            uri (str): URI generated from ConfigParser.get_config() ("ROUTER_URI" key).

        Returns:
            Optional[Client]: The client object used to interact with the API
                or None if it can't connect to the API.
        """

        client = None

        try:
            client = Client(AuthorizedConnection(uri))
            logger.info("Successfully connected to the router")

        except HuaweiExceptions.ResponseErrorLoginRequiredException:
            logger.warning("Expired session, login again in the next loop")

        except HuaweiExceptions.LoginErrorAlreadyLoginException:
            logger.warning(textwrap.dedent(f"""\
                Client is already logged in but a new attempt has been made,
                wait until the Huawei router automatically disconnect old clients.
                """))

        except Exception as err:
            logger.critical(f"Router connection failed! Please check the config settings\n{err}")
            sys.exit(1)

        return client


    @staticmethod
    def api_connection_loop(client: Optional[Client], uri: str) -> Client:
        """
        Try to connect to the API using a loop and a time sleeping system.

        Args:
            client (Client, optional): Recursively assign the client var and check if connected.
            uri (str): URI generated from ConfigParser.get_config() ("ROUTER_URI" key).

        Returns:
            Client: The connected client.
        """

        # Infinite loop limit
        inf_loop_limit = 12
        iteration = 0

        while client is None:
            logger.info("Trying to connect to the router..")
            client = HuaweiWrapper.connect_to_api(uri)

            if iteration > inf_loop_limit:
                error_msg = textwrap.dedent(f"""\
                Could not connect to the router after {iteration} attempts.

                Debugging:
                - Verify the settings inside the YAML config file and if your Huawei router is online.
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

                logger.critical(error_msg)
                sys.exit(1)

            iteration += 1

            # New attempt every 5 seconds
            if client is None:
                time.sleep(5)

        return client


    @staticmethod
    def disconnect(client: Optional[Client]):
        """
        Try-except disconnection from the Huawei Router.

        Args:
            client (Client, optional): To test if the client is already connected.
        """

        try:
            # If client instance exists, disconnect from the router
            if client is not None:
                client.user.logout()
                AppHistory.save_history()
                print("\n")
                logger.info("Successfully disconnected from the router")
        except Exception:
            pass

        sys.exit(1)


    @staticmethod
    def unique_sms_id_check(sms: Optional[dict[str, str]]) -> bool:
        """
        Used to avoid sending the same SMS multiple times
        in the case of a SMS received at the exact same time as a new iteration.

        Note:
            Saves the last SMS ID and verify that it is not already sent.

        Args:
            sms (dict[str, str], optional): The last received SMS dict.

        Returns:
            bool: True if the SMS can be sent.
        """

        if sms is not None and "Index" in sms.keys():
            ID = sms["Index"]

            if ID != HuaweiWrapper.last_received_sms_id:
                HuaweiWrapper.last_received_sms_id = ID
                return True

        return False


    @staticmethod
    def is_sms_whitelisted(sender: str, whitelist: list[str]) -> bool:
        """
        Returns True if the SMS is sent by one of the senders is inside the whitelist.

        Note:
            If the whitelist system is deactivated (empty list), it always returns True.

        Args:
            sender (str): The SMS sender.
            whitelist (list[str]): The list of whitelisted senders.

        Returns:
            bool: True if the SMS is sent by one of the whitelisted senders.
        """

        if len(whitelist) > 0:
            for included_sender in whitelist:
                if sender == included_sender:
                    return True

            return False

        return True


    @staticmethod
    def get_last_sms(
        client: Client,
        contacts: dict[str, str],
        ignore_read: bool = True,
        dont_set_to_read: bool = False
    ) -> Optional[dict[str, str]]:
        """
        Returns the last sms received by the router with unread priority.

        Note:
            Also adds a "Contact" field to the SMS dict if the sender is inside the contacts dict.

        Args:
            client (Client): The API client.
            contacts (dict[str, str]): The contacts dict.
            ignore_read (bool): If True, ignores already read SMS.
            dont_set_to_read (bool): If True, doesn't set the SMS to read (defaults to False).

        Returns:
            Optional[dict[str, str]]: A dict containing all the SMS info,
                None if no SMS found or if the SMS is already read and "ignore_read" is set to True.
        """

        sms: Optional[dict[str, str]] = None

        try:
            # Get last received SMS (Unread priority)
            raw_sms_list = client.sms.get_sms_list(
                1,
                BoxTypeEnum.LOCAL_INBOX,
                1,
                SortTypeEnum.PHONE,
                False,
                True
            )

            sms_read_state = 0

            # If there is at least one SMS
            if raw_sms_list["Count"] != "0":
                # Get the last SMS
                raw_last_sms = raw_sms_list["Messages"]["Message"][0]

                # Get the read state & the SMS dict
                sms_read_state = int(raw_last_sms["Smstat"])
                sms = raw_last_sms

            # SMS already read
            if ignore_read and sms_read_state == 1:
                sms = None

            # Verify that the last sent SMS have not the same ID
            is_sms_unique = HuaweiWrapper.unique_sms_id_check(sms)

            if sms is not None and is_sms_unique:
                # Get useful SMS data
                sms_sender = sms["Phone"]

                # Set the SMS status to read
                if not dont_set_to_read:
                    client.sms.set_read(int(sms["Index"]))

                # Main Log
                logger.info(f"New SMS received from {sms_sender}")
            else:
                logger.info("No new SMS found..")

        except Exception as err:
            logger.error(f"Last SMS received by the router cannot be returned\n{err}")
            return None

        # If the sender is inside the contacts dict, add a "Contact" field to the SMS dict
        if sms is not None:
            formatted_phone_number = ConfigParser.format_phone_number(sms["Phone"])

            if formatted_phone_number in contacts.keys():
                sms["Contact"] = contacts[formatted_phone_number]

        return sms


    @staticmethod
    def format_date(sms_date: str) -> str:
        """
        Used to format the date inside the forwarded SMS.

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
    def format_sms(sms: dict[str, str]) -> str:
        """
        Use the SMS dict info to format a messages used for the forwarding.

        Args:
            sms (dict[str, str]): Original SMS dict.

        Returns:
            str: Formatted string of the message.
        """

        # Get SMS info
        sms_date = HuaweiWrapper.format_date(sms["Date"])
        sms_content = sms["Content"]

        if "Contact" in sms.keys():
            sms_sender = sms["Contact"]
        else:
            sms_sender = sms["Phone"]

        return f"[{sms_date}] New SMS from '{sms_sender}':\n\n{sms_content}"


    @staticmethod
    def send_sms(client: Client, sms_content: str, phone_number: str) -> bool:
        """
        Allows to send an SMS to a number (international formatted such as "+33937023216").

        Args:
            client (Client): Returned from HuaweiWrapper.api_connection_loop().
            sms_content (str): Content of the original SMS dictionary.
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
            logger.error(f"SMS cannot be sent to {phone_number}\n{error_reason}")
        else:
            logger.info(f"SMS correctly sent to {phone_number}")

        return gen_state


    @staticmethod
    def sms_forwarder(
        client: Client,
        sms: Optional[dict[str, str]],
        forwarders: dict[str, list[str]]
    ) -> bool:
        """
        Allows to forward a formatted SMS to multiple phone numbers,
        includes contacts & history systems.

        Args:
            client (Client): Returned from HuaweiWrapper.api_connection_loop().
            sms (Optional[dict[str, str]]): Original SMS dictionary.
            forwarders (dict[str, list[str]]): Dict of phone numbers to forward the SMS to.

        Returns:
            bool: If the message has successfully been forwarded.
        """

        if sms is not None and "Index" in sms:
            api_res = True

            # Avoid duplicata
            if sms["Index"] != HuaweiWrapper.last_sent_sms_id:
                sms_content = HuaweiWrapper.format_sms(sms)

                # Forwarding to every listed number
                for forwarder in forwarders.keys():
                    is_whitelisted = HuaweiWrapper.is_sms_whitelisted(sms["Phone"], forwarders[forwarder]) # type: ignore

                    # Check if the number is whitelisted
                    if is_whitelisted:
                        api_response = HuaweiWrapper.send_sms(client, sms_content, forwarder)

                        if not api_response:
                            api_res = False
                        else:
                            AppHistory.add_to_history(sms)
                    else:
                        logger.warning(f"SMS from {sms['Phone']} has been ignored (not whitelisted)")

                return api_res
            else:
                logger.warning("This SMS seems to have been already sent once")

        return False


    @staticmethod
    def sms_replier(
        client: Client,
        sms: Optional[dict[str, str]],
        repliers: dict[str, str]
    ) -> bool:
        """
        Allows to reply to a SMS with a filter inside of it, with a custom message.

        Args:
            client (Client): Returned from HuaweiWrapper.api_connection_loop().
            sms (Optional[dict[str, str]]): Original SMS dictionary.
            repliers (dict[str, str]): Dict of filters and replies.

        Returns:
            bool: If the reply has successfully been sent.
        """

        if sms is not None and "Index" in sms:
            # If the phone number is inside the repliers dict
            if sms["Phone"] in repliers.keys():
                print("SMS Replier:", sms["Phone"])
                print("Repliers:", repliers)

                replier = repliers[sms["Phone"]]

                print("Replier:", replier)

                # Get all the filtered messages and their replies
                for message in replier:
                    sms_content = sms["Content"].lower()

                    print("SMS Content:", sms_content)
                    print("Message Filter:", message["filter"]) # type: ignore

                    # Check if the message contains the filter
                    if message["filter"].lower() in sms_content: # type: ignore
                        test = HuaweiWrapper.send_sms(
                            client,
                            message["reply"], # type: ignore
                            sms["Phone"]
                        )

                        print("Is the SMS properly sent:", test)

                        AppHistory.add_to_history(sms)

                        return True

        return False