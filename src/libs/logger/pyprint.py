from inspect import currentframe, getouterframes
from colorama import Style, Fore, init
from typing import Any
import time


class LogTypes():
    '''Contains all the available log types for the pyprint() function.
    These types comes with a short version, every output type will have the same length (4 chars).

    Available types:
        - [CRIT] CRITICAL
        - [ERRO] ERROR
        - [WARN] WARN
        - [SCES] SUCCESS
        - [SILT] SILENT
        - [REDY] READY
        - [DATA] DATA
        - [INFO] INFO
    '''

    CRITICAL = {'longName': 'CRITICAL', 'shortName': 'CRIT', 'typeColor': Fore.LIGHTRED_EX,     'msgColor': Fore.LIGHTRED_EX}
    ERROR    = {'longName': 'ERROR',    'shortName': 'ERRO', 'typeColor': Fore.RED,             'msgColor': Fore.RED}
    WARN     = {'longName': 'WARN',     'shortName': 'WARN', 'typeColor': Fore.YELLOW,          'msgColor': Fore.YELLOW}
    SUCCESS  = {'longName': 'SUCCESS',  'shortName': 'SCES', 'typeColor': Fore.LIGHTGREEN_EX,   'msgColor': Fore.LIGHTGREEN_EX}
    SILENT   = {'longName': 'SILENT',   'shortName': 'SILT', 'typeColor': Fore.LIGHTBLACK_EX,   'msgColor': Fore.LIGHTBLACK_EX}
    READY    = {'longName': 'READY',    'shortName': 'REDY', 'typeColor': Fore.LIGHTMAGENTA_EX, 'msgColor': Fore.LIGHTMAGENTA_EX}
    DATA     = {'longName': 'DATA',     'shortName': 'DATA', 'typeColor': Fore.LIGHTCYAN_EX,    'msgColor': Fore.LIGHTCYAN_EX}
    INFO     = {'longName': 'INFO',     'shortName': 'INFO', 'typeColor': Fore.LIGHTBLUE_EX,    'msgColor': Fore.LIGHTBLUE_EX}


class __Settings:
    # Verbose mode for printing
    VERBOSE_DEBUGGING: bool = True

    # Short mode for printing (log types of 4 chars)
    SHORT_DEBUGGING: bool = False

    # Type functionalities
    FORCED_TYPES = [
        LogTypes.SUCCESS,
        LogTypes.WARN,
        LogTypes.ERROR,
        LogTypes.CRITICAL
    ]
    SHOW_FUNCTION_NAME_TYPES = [
        LogTypes.WARN,
        LogTypes.ERROR,
        LogTypes.CRITICAL
    ]


def set_verbose(state: bool):
    '''Change the state of the verbose debugging (Set to True by default).
    Verbose debugging simply means that all available log types are printed into the console.

    If turned off, only main log types will be printed:
        - CRITICAL
        - ERROR
        - WARN
        - SUCCESS.
    '''

    __Settings.VERBOSE_DEBUGGING = state


def set_short(state: bool):
    '''Change the state of the short debugging (Set to False by default).
    Short debugging simply means that log types in the log only contains 4 chars.

    Examples:
        - "[CRITICAL] Message.." -> "[CRIT] Message.."
        - "[SILENT] Message.." -> "[SILT] Message.."

    This allows to print messages with the same starting point,
    it's useful if you have a lot of print statements, it makes it more readable.
    '''

    __Settings.SHORT_DEBUGGING = state


def new_log_type(
    long_name: str,
    short_name: str,
    type_color: str = Fore.WHITE,
    msg_color: str = Fore.WHITE
) -> dict[str, str]:
    '''Allows to define a new log type as a dict,
    The value is returned and can be saved into a type var.

    Args:
        long_name (str): The long version of the log type name (Used by default).
        short_name (str): The short version of the log type name (if set_short(True)).
        msg_color (Back.COLOR / Fore.COLOR, optional): Color of the message itself.
        type_color (Back.COLOR / Fore.COLOR, optional): Color of the type that comes before the msg.

    Returns:
        dict: A logtype dict.
    '''

    return {
        'longName': long_name,
        'shortName': short_name,
        'typeColor': type_color,
        'msgColor': msg_color
    }



def new_section(
    section_title: str = 'PYOSTRA DEBUGGING',
    skip_line: bool = True,
    section_title_color: str = Fore.LIGHTBLUE_EX,
    separator_char: str = '=',
    separators_amount: int = 35,
):
    '''Show a new section title, to separate different part during the debugging.
    Sections allows to separate different types of console logs.

    Example:
        ============= NEW SECTION =============

    Note:
        All the parameters are optional and can be used to customize the section title.

    Args:
        section_title (str, optional): The title of the current section.
        skip_line (bool, optional): If True, skip a line before the title.
        section_title_color (str, optional): Use Colorama for that (Fore.LIGHTBLUE_EX for example).
        separator_char (str, optional): The character used by the section title (see the example).
        separators_amount (int, optional): The amount of separators for the title.
    '''

    separators = separator_char * separators_amount
    separated_title = f'{separators} {section_title} {separators}'
    output = f'{section_title_color}{separated_title}{Style.RESET_ALL}'

    if skip_line:
        output = f'\n{output}'
    print(output)


def __internal_error(log_msg: str):
    print(f'{Fore.LIGHTRED_EX}[PYOSTRA_ERROR] {log_msg}{Style.RESET_ALL}')


def pyprint(
    log_type: dict[str, str],
    log_msg: Any,
    disable_function_name: bool = False,
    on_same_line: bool = False,
    force_verbose: bool = False
):
    '''Pyostra formatted print statements.

    The "log_type" argument needs a dict that comes from the "LogTypes" class.
    But you can also define your own log type by using the new_log_type() function.

    Supported log types by default:
        - [CRIT] CRITICAL
        - [ERRO] ERROR
        - [WARN] WARN
        - [SCES] SUCCESS
        - [SILT] SILENT
        - [REDY] READY
        - [DATA] DATA
        - [INFO] INFO

    Note:
        By default, critical errors and normal errors also prints the name of the calling function,
        "disable_function_name" simply allows you to bypass/disable that for a specific log.

    Args:
        log_type (str): Type of the log (Unsupported log type returns white colored log).
        log_msg (str): The main message of the log.
        disable_function_name (bool, optional): Allows to specifically disable the printing
            of the caller's name for errors & warnings.
        on_same_line (bool, optional): Print on the same line as before.
        force_verbose (bool, optional): Force the log inside the terminal,
            not depending on the log type when verbose debugging is turned off.
    '''

    # Verbose debugging, forced log type or forced verbose
    if (__Settings.VERBOSE_DEBUGGING
        or (not __Settings.VERBOSE_DEBUGGING and log_type in __Settings.FORCED_TYPES)
        or force_verbose
    ):
        # Validate the log_type dict
        if type(log_type) == dict:
            if set(('longName', 'shortName', 'typeColor', 'msgColor')) <= log_type.keys():
                long_name = log_type['longName']
                short_name = log_type['shortName']
                type_color = log_type['typeColor']
                msg_color = log_type['msgColor']
            else:
                __internal_error(f'Invalid log type key error: {log_type}')
                return
        else:
            __internal_error(f'Specified log type is not a dict: {log_type}')
            return

        # Short log type debugging
        if __Settings.SHORT_DEBUGGING:
            log_type_name = short_name
        else:
            log_type_name = long_name

        # Show the caller's name
        if log_type not in __Settings.SHOW_FUNCTION_NAME_TYPES or disable_function_name:
            function_name = ''
        else:
            cur_frame = currentframe()
            out_frame = getouterframes(cur_frame, 2)
            name = out_frame[1][3]

            if name != '<module>':
                name = f'{name}():'
            else:
                name = 'Module:'

            function_name = f' {name}'

        # Print on the previous line
        if on_same_line:
            end_char = '\r'
        else:
            end_char = None

        # Final print statement
        init(True)
        log_title = f'{type_color}[{log_type_name}]'
        print(f'{log_title}{msg_color}{function_name} {log_msg}', end=end_char)


def extime(
    timer_name: str,
    perf_counter_ns_value: int,
    multiply_timer: int = 1,
    approximated_value: bool = False,
):
    '''Automatic timer format (ns, µs, ms, s and mins units).

    Args:
        timer_name (str): Name of the timer.
        perf_counter_ns_value (int): Using time.perf_counter_ns() to get the starting value of the timer.
        multiply_timer (int, optional): Multiply the time by a value (To estimate time for x iterations).
        approximated_value (bool, optional): If True, adds the "~" character to show that it's an approximation.

    Returns:
        str: The formatted timer message
    '''

    timer = (time.perf_counter_ns() - perf_counter_ns_value) * multiply_timer

    units = ['ns', 'µs', 'ms', 's', ' mins']
    powers = [10**3, 10**6, 10**9]
    res = 0
    i = 0

    if timer < powers[0]:
        res = timer
    elif powers[0] <= timer < powers[1]:
        res = round(timer / powers[0])
        i = 1
    elif powers[1] <= timer < powers[2]:
        res = round(timer / powers[1])
        i = 2
    elif powers[2] <= timer:
        res = timer / powers[2]
        i = 3

        # Using minutes instead
        if res > 120:
            res = round(res / 60)
            i = 4

    res = round(res, 2)

    if approximated_value:
        output = f'{timer_name}: ~{res}{units[i]}'
    else:
        output = f'{timer_name}: {res}{units[i]}'

    pyprint(LogTypes.SUCCESS, output)