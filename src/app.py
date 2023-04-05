from libs.huawei_wrapper import HuaweiWrapper
from libs.config_parser import ConfigParser
from libs.app_history import AppHistory
from libs import logger

import time


client = None
config = ConfigParser.get_config()
history = AppHistory.load_history()

while True:
    try:
        client = HuaweiWrapper.api_connection_loop(client, config["ROUTER_URI"]) # type: ignore
        last_sms = HuaweiWrapper.get_last_sms(client, config["CONTACTS"], True, False) # type: ignore

        # Main SMS forwarding function
        HuaweiWrapper.sms_forwarder(
            client,
            last_sms,
            config["FORWARDERS"] # type: ignore
        )

        # Main SMS replying function
        HuaweiWrapper.sms_replier(
            client,
            last_sms,
            config["REPLIERS"] # type: ignore
        )

        # Saves the history every loop
        if history:
            AppHistory.save_history()

        time.sleep(config["ROUTER_LOOP_SLEEP"]) # type: ignore

    # Disconnect from the router if possible
    except KeyboardInterrupt:
        HuaweiWrapper.disconnect(client)
    except Exception as err:
        logger.critical(f"Something went wrong!\n{err}")
        HuaweiWrapper.disconnect(client)
