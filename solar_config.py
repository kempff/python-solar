import os

LOG_FILE_PATH = os.getenv('LOG_FILE_PATH','/tmp/')
LOG_LEVEL = os.getenv('LOG_LEVEL','WARNING')
INFLUX_HOST = os.getenv('INFLUX_HOST','localhost')
INFLUX_PORT = os.getenv('INFLUX_PORT','8086')
INFLUX_DB = os.getenv('INFLUX_DATABASE','solardb')
PROCESS_TIME = int(os.getenv('PROCESS_TIME', 60))
INSTALLATION = os.getenv('INSTALLATION', "test_installation1")
TIME_OFFSET = int(os.getenv('TIME_OFFSET', 2))

if os.getenv('DEBUG_MODE', False) == 'True':
    DEBUG_MODE = True
else:
    DEBUG_MODE = False

ERROR_MESSAGES = {
    1: {
        'message': 'Reserved',
        'severity': 'error',
    },
    2: {
        'message': 'Inverter fault',
        'severity': 'error',
    },
    3: {
        'message': 'Bus Over',
        'severity': 'error',
    },
    4: {
        'message': 'Bus Under',
        'severity': 'error',
    },
    5: {
        'message': 'Bus Soft Fail',
        'severity': 'error',
    },
    6: {
        'message': 'Line Fail',
        'severity': 'warning',
    },
    7: {
        'message': 'OPV Short',
        'severity': 'warning',
    },
    8: {
        'message': 'Inverter voltage too low',
        'severity': 'error',
    },
    9: {
        'message': 'Inverter voltage too high',
        'severity': 'error',
    },
    10: {
        'message': 'Over temperature',
        'severity': 'error',
    },
    11: {
        'message': 'Fan locked',
        'severity': 'error',
    },
    12: {
        'message': 'Battery voltage high',
        'severity': 'error',
    },
    13: {
        'message': 'Battery low alarm',
        'severity': 'warning',
    },
    14: {
        'message': 'Reserved',
        'severity': 'error',
    },
    15: {
        'message': 'Battery under shutdown',
        'severity': 'warning',
    },
    16: {
        'message': 'Battery derating',
        'severity': 'warning',
    },
    17: {
        'message': 'Overload',
        'severity': 'error',
    },
    18: {
        'message': 'Eeprom fault',
        'severity': 'warning',
    },
    19: {
        'message': 'Inverter Over Current',
        'severity': 'error',
    },
    20: {
        'message': 'Inverter Soft Fail',
        'severity': 'error',
    },
    21: {
        'message': 'Self Test Fail',
        'severity': 'error',
    },
    22: {
        'message': 'OP DC Voltage Over',
        'severity': 'error',
    },
    23: {
        'message': 'Bat Open',
        'severity': 'error',
    },
    24: {
        'message': 'Current Sensor Fail',
        'severity': 'error',
    },
    25: {
        'message': 'Battery Short',
        'severity': 'error',
    },
    26: {
        'message': 'Power limit',
        'severity': 'warning',
    },
    27: {
        'message': 'PV voltage high 1',
        'severity': 'warning',
    },
    28: {
        'message': 'MPPT overload fault 1',
        'severity': 'warning',
    },
    29: {
        'message': 'MPPT overload warning 1',
        'severity': 'warning',
    },
    30: {
        'message': 'Battery too low to charge 1',
        'severity': 'warning',
    },
    31: {
        'message': 'PV voltage high 2',
        'severity': 'warning',
    },
    32: {
        'message': 'MPPT overload fault 2',
        'severity': 'warning',
    },
}