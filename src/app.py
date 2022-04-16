from libs import HuaweiWrapper

import time
import sys
import os


main_env_dict = HuaweiWrapper.get_formatted_env()

client = HuaweiWrapper.connect_to_api(main_env_dict["URI"])

# if client.sms.send_sms([main_env_dict["RECEIVER_PHONE_NUMBER"]], "Yo") == "OK":
#     print("SMS success")
    
print(HuaweiWrapper.get_last_sms(client, False))