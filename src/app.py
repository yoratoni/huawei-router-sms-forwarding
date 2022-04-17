from libs import HuaweiWrapper, AppUtils

import time


client = None
system_dict = HuaweiWrapper.get_formatted_env()

while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, system_dict["URI"])
        last_sms = HuaweiWrapper.get_last_sms(client, system_dict["SENDERS_WHITELIST"])
        
        if last_sms is not None and "Content" in last_sms:
            formatted_sms = HuaweiWrapper.format_sms(last_sms)
            HuaweiWrapper.send_sms(client, system_dict["USER_PHONE_NUMBER"], formatted_sms)
        
        time.sleep(system_dict["LOOP_DELAY"])
        
    except KeyboardInterrupt:
        try:
            # Disconnect before program ends
            if client is not None:
                client.user.logout()
        except Exception:
            pass
