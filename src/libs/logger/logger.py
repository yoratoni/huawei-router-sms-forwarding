import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a formatter with color
class Formatter(logging.Formatter):
    COLORS = {
        'CRITICAL': '\033[1;31m',  # bold red
        'ERROR': '\033[0;31m',     # red
        'WARNING': '\033[0;33m',   # yellow
        'INFO': '\033[0;32m',      # green
        'DEBUG': '\033[0;37m',     # white
        'RESET': '\033[0m'         # reset color
    }

    def format(self, record: logging.LogRecord):
        levelname = record.levelname
        message = super().format(record)
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        time_str = self.formatTime(record, self.datefmt)

        return f"{color}[{time_str}] [{record.levelname}] {message}{self.COLORS['RESET']}"

# Set the logger level and formatter
log_format = '%(message)s'
formatter = Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Examples
# logger.debug('Debug message')
# logger.info('Info message')
# logger.warning('Warning message')
# logger.error('Error message')
# logger.critical('Critical message')