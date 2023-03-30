from libs import HuaweiWrapper, EnvParsing, AppHistory
from libs.logger import pyprint, LogTypes

import time

#
client = None
system_dict = EnvParsing.get_formatted_env()
AppHistory.load_history()

while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, system_dict["URI"]) # type: ignore
        last_sms = HuaweiWrapper.get_last_sms(client, system_dict["SENDERS_WHITELIST"]) # type: ignore

        # Main SMS forwarding function
        HuaweiWrapper.forward_sms(
            client,
            last_sms,
            system_dict["CONTACTS"], # type: ignore
            system_dict["USER_PHONE_NUMBER"] # type: ignore
        )

        # Saves the history every loop
        AppHistory.save_history()

        time.sleep(system_dict["LOOP_DELAY"]) # type: ignore

    # Disconnect from the router if possible
    except KeyboardInterrupt:
        HuaweiWrapper.disconnect(client)
    except Exception as err:
        pyprint(LogTypes.CRITICAL, f"Something went wrong! [{err}]")
        HuaweiWrapper.disconnect(client)
