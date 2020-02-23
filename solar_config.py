import os

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH','/tmp/')
LOG_LEVEL = os.getenv('LOG_LEVEL','WARNING')
PRINT_LOGS = bool(os.getenv('PRINT_LOGS', False))
INFLUX_HOST = os.getenv('INFLUX_HOST','localhost')
INFLUX_PORT = os.getenv('INFLUX_PORT','8086')
INFLUX_DB = os.getenv('INFLUX_DATABASE','solardb')
PROCESS_TIME = int(os.getenv('PROCESS_TIME', 60))
INSTALLATION = os.getenv('INSTALLATION', "test_installation1")
TIME_OFFSET = int(os.getenv('TIME_OFFSET', 2))

# Flask configuration
FLASK_HTTP_PORT = os.getenv('FLASK_HTTP_PORT', 8080)
FLASK_HTTP_HOST = os.getenv('FLASK_HTTP_HOST', '0.0.0.0')

# API authentication
BASIC_AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME', '')
BASIC_AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD', '')

if os.getenv('DEBUG_MODE', False) == 'True':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False
