import structlog
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from inspect import getframeinfo, stack
from .settings import APP_NAME, APP_VERSION

# Logging configuration
DEFAULT_LOGGING_LEVEL = os.getenv('DEFAULT_LOGGING_LEVEL', logging.WARNING)
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/tmp/')

class _StructLogger:

    '''
    Logger class. Don't call this, use the 'StructLogger' which returns a singleton (one logging object).
    The class has overloaded the logger functions to add the calling applications filename and line number.
    '''
    def __init__(self, app_name=APP_NAME):
        self.logger = structlog.stdlib.BoundLogger
        # Setup the logging configuration
        chain = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]

        structlog.configure_once(
                processors=chain,
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

        logging.basicConfig(format='%(message)s', stream=sys.stdout, level=int(DEFAULT_LOGGING_LEVEL))
        self.app_name = app_name
        self.logger = structlog.get_logger(self.app_name)

        # Add logging to Rotating Log as well
        log_file_path = LOG_FILE_PATH
        file_handler = RotatingFileHandler(log_file_path + self.app_name + '.log', maxBytes=2 * 1024 * 1024, backupCount=10)
        formatter = logging.Formatter('{ "loggerName":"%(name)s", "timestamp":"%(asctime)s", '
                                    '"levelName":"%(levelname)s", "pathName":"%(pathname)s", '
                                    '"functionName":"%(funcName)s", "lineNo":"%(lineno)d", "message":"%(message)s"}')
        file_handler.formatter = formatter
        self.logger.addHandler(file_handler)

    def print_app_version(self,app_version=APP_VERSION):
        self.logger.setLevel(logging.INFO)
        self.logger.info(f'Running app \'{self.app_name}\' version {app_version}')
        self.logger.setLevel(int(DEFAULT_LOGGING_LEVEL))

    def critical(self, log_text):
        caller = getframeinfo(stack()[1][0])
        self.logger.critical(f'-< {os.path.basename(caller.filename)}:{caller.lineno} >- {log_text}')

    def error(self, log_text):
        caller = getframeinfo(stack()[1][0])
        self.logger.error(f'-< {os.path.basename(caller.filename)}:{caller.lineno} >- {log_text}')

    def warning(self, log_text):
        caller = getframeinfo(stack()[1][0])
        self.logger.warning(f'-< {os.path.basename(caller.filename)}:{caller.lineno} >- {log_text}')

    def info(self, log_text):
        caller = getframeinfo(stack()[1][0])
        self.logger.info(f'-< {os.path.basename(caller.filename)}:{caller.lineno} >- {log_text}')

    def debug(self, log_text):
        caller = getframeinfo(stack()[1][0])
        self.logger.debug(f'-< {os.path.basename(caller.filename)}:{caller.lineno} >- {log_text}')

    def setLevel(self, level):
        self.logger.setLevel(level)

# Create a logging object 
_struct_logger = _StructLogger()

def StructLogger():
    '''
    Use this function to get the single logger instance to use.
    '''
    return _struct_logger
