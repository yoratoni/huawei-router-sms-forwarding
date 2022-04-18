from libs import HuaweiWrapper, AppUtils

import time
import sys


client = None
last_sms_ID = ""
system_dict = AppUtils.get_formatted_env()


while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, system_dict["URI"])
        last_sms = HuaweiWrapper.get_last_sms(client, system_dict["SENDERS_WHITELIST"])
        
        print(last_sms)
        
        if last_sms is not None and "Content" in last_sms:
            formatted_sms = HuaweiWrapper.format_sms(system_dict["CONTACTS"], last_sms)
            # HuaweiWrapper.send_sms(client, system_dict["USER_PHONE_NUMBER"], formatted_sms)
            print(formatted_sms)
        
        time.sleep(system_dict["LOOP_DELAY"])
        
    except KeyboardInterrupt:
        try:
            # Disconnect before program ends
            if client is not None:
                client.user.logout()
        except Exception:
            pass

        sys.exit(1)
