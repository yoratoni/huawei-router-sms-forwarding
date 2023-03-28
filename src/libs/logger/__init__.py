'''Encapsulation of all the Ostra python environment main functions.

This module provides a custom formatted logging system,
it also implements a formatted performance output system (extime).

set_verbose(): if True, prints all the available log messages.
In the other case, prints only important messages depending on the log type (Such as Warn, Error and Critical).

set_short(): As the log type is printed at the start of every log,
If set to True, it reduces the log types to 4 chars only, making it more readable if you have a lot of printing.

new_log_type(): Defines a new type using Colorama colors (it returns a dict that can be used as an arg for pyprint())

new_section(): Used to separate different types of logs.

pyprint(): The main custom formatted print statements.

extime(): Using time.perf_counter_ns(), returns a formatted value of the time.
'''


from libs.logger.pyprint import LogTypes
from libs.logger.pyprint import set_verbose
from libs.logger.pyprint import set_short
from libs.logger.pyprint import new_log_type
from libs.logger.pyprint import new_section
from libs.logger.pyprint import pyprint
from libs.logger.pyprint import extime