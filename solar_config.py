import os

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH','/home/pi/Projects/python-solar/log/')
# TODO put back to warning
LOG_LEVEL = os.getenv('LOG_LEVEL','DEBUG')
INFLUX_HOST = os.getenv('INFLUX_HOST','localhost')
INFLUX_PORT = os.getenv('INFLUX_PORT','8086')
INFLUX_DB = os.getenv('INFLUX_DATABASE','solardb')
DEBUG_MODE = os.getenv('DEBUG_MODE', False)
