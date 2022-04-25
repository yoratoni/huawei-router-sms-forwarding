from libs import HuaweiWrapper, EnvParsing, AppHistory
from pyostra import pyprint, LogTypes

import time
import sys
import os

client = None
system_dict = EnvParsing.get_formatted_env()
AppHistory.load_history()


while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, system_dict["URI"])
        last_sms = HuaweiWrapper.get_last_sms(client, system_dict["SENDERS_WHITELIST"])

        # Main SMS forwarding function
        HuaweiWrapper.forward_sms(
            client,
            last_sms,
            system_dict["CONTACTS"],
            system_dict["USER_PHONE_NUMBER"]
        )
        
        # Saves the history every loop
        AppHistory.save_history()
        
        time.sleep(system_dict["LOOP_DELAY"])
    
    # Disconnect from the router if possible
    except KeyboardInterrupt:
        HuaweiWrapper.disconnect(client)
    except Exception as err:
        pyprint(LogTypes.CRITICAL, f"Something went wrong! [{err}]")
        HuaweiWrapper.disconnect(client)
        