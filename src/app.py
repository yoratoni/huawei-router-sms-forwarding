from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.Connection import Connection
from huawei_lte_api.Client import Client
from huawei_lte_api.api.User import User

import huawei_lte_api.exceptions


# Main loop
while True:
    try:
        pass
    except huawei_lte_api.exceptions.ResponseErrorLoginRequiredException as e:
        print(_('Session timeout, login again!'))
    except huawei_lte_api.exceptions.LoginErrorAlreadyLoginException as e:
        client.user.logout()
    except Exception as e:
        print(_('Router connection failed! Please check the settings. \nError message:\n{error_msg}').format(error_msg=e))