import os

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH','/home/pi/Projects/python-solar/log/')
LOG_LEVEL = os.getenv('LOG_LEVEL','WARNING')
PRINT_LOGS = os.getenv('PRINT_LOGS', False)
INFLUX_HOST = os.getenv('INFLUX_HOST','localhost')
INFLUX_PORT = os.getenv('INFLUX_PORT','8086')
INFLUX_DB = os.getenv('INFLUX_DATABASE','solardb')
DEBUG_MODE = os.getenv('DEBUG_MODE', False)
