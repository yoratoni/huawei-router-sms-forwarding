from libs import HuaweiWrapper, AppUtils
from pyostra import pyprint, LogTypes

import time
import sys


client = None
system_dict = AppUtils.get_formatted_env()


while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, system_dict["URI"])
        last_sms = HuaweiWrapper.get_last_sms(client, system_dict["SENDERS_WHITELIST"])

        if last_sms is not None and "Content" in last_sms:
            formatted_sms = HuaweiWrapper.format_sms(system_dict["CONTACTS"], last_sms)
            # HuaweiWrapper.send_sms(client, system_dict["USER_PHONE_NUMBER"], formatted_sms)
        
        time.sleep(system_dict["LOOP_DELAY"])
    
    # Disconnect from the router if possible
    except KeyboardInterrupt:
        HuaweiWrapper.disconnect(client)
