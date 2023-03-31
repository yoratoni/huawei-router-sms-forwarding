from libs import HuaweiWrapper, AppHistory, ConfigParser
from libs.logger import pyprint, LogTypes

import time


client = None
config = ConfigParser.get_config()
AppHistory.load_history()

while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, config["ROUTER_URI"]) # type: ignore
        last_sms = HuaweiWrapper.get_last_sms(client, config["CONTACTS"], True) # type: ignore

        # Main SMS forwarding function
        HuaweiWrapper.forward_sms(
            client,
            last_sms,
            config["FORWARDERS"] # type: ignore
        )

        # Saves the history every loop
        AppHistory.save_history()

        time.sleep(config["ROUTER_LOOP_SLEEP"]) # type: ignore

    # Disconnect from the router if possible
    except KeyboardInterrupt:
        HuaweiWrapper.disconnect(client)
    # except Exception as err:
    #     pyprint(LogTypes.CRITICAL, f"Something went wrong! [{err}]")
    #     HuaweiWrapper.disconnect(client)
