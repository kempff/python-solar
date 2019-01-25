# Python reader for solar panel controller

import evdev
from influxdb import InfluxDBClient
import schedule
import logging
import time
import solar_config as config
import sys
from logging.handlers import RotatingFileHandler
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QApplication
from ui.python_ui import Ui_MainWindow

influx_client = InfluxDBClient(config.INFLUX_HOST, config.INFLUX_PORT, database=config.INFLUX_DB)

debug_data = config.DEBUG_MODE
write_to_db = True

if debug_data:
    # Open the files for reading
    pigs_file = open("qpigs.txt","r")
    mod_file = open("qmod.txt","r")
    piri_file = open("qpiri.txt","r")

mode_data = []          # From QMOD command
status_data = []        # From QPIGS command
ratings_data = []       # From QPIRI command
# Setup logging, using the configuration to set the path and the level
log_file_path = config.LOG_FILE_PATH
file_handler = RotatingFileHandler(log_file_path + 'python_solar.log', maxBytes=2 * 1024 * 1024, backupCount=10)
log_level_config = config.LOG_LEVEL
log_level = logging.WARNING
if log_level_config == 'INFO':
    log_level = logging.INFO
elif log_level_config == 'DEBUG':
    log_level = logging.DEBUG
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(
    '\n\n** %(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]')
)
logger = logging.getLogger('python_solar')
logger.setLevel(log_level)
logger.addHandler(file_handler)


# Read next line from each file, if at end of the file loop to the beginning
def read_file_data(input_file):
    return_data = []
    return_data = input_file.readline()
    if return_data is "":
        input_file.seek(0)
        return_data = input_file.readline()
    return return_data
    

# Read data function (either from USB or file)
def read_data():
    global mode_data
    global status_data
    global ratings_data
    if debug_data:
        mode_data = read_file_data(mod_file).split()
        logger.info("Mode data: {0}".format(mode_data))
        status_data = read_file_data(pigs_file).split()
        logger.info("Status data: {0}".format(status_data))
        ratings_data = read_file_data(piri_file).split()
        logger.info("Ratings data: {0}".format(ratings_data))
    else:
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
            logger.info("{0} - {1} - {2} ".format(device.fn, device.name, device.phys))



def populate_mode_data(mode_data, client):
    mode_dictionary = { 'P': 'Power on', 'S': 'Standby', 'L': 'Line',
                        'B': 'Battery', 'F': 'Fault', 'H': 'Power saving'}
    mode_body = [
    {
        "measurement": "system_mode",
        "tags": {
            "host": "test_installation1"
            },
        "fields": {
            "mode": "unknown"
            }
    }
    ]
    if mode_data[0] in mode_dictionary.keys():
        mode_body[0]['fields']['mode'] = mode_dictionary[mode_data[0]]
        client.write_points(mode_body)
    else:
        logger.error("Invalid mode {0}".format(mode_data[0]))
    
        
def populate_status_data(status_data, client):
    status_body = [
    {
        "measurement": "system_status",
        "tags": {
            "host": "test_installation1"
            },
        "fields": {
            "grid_voltage": 123.4,
            "grid_frequency": 50.0,
            "ac_output_voltage": 123.5,
            "ac_output_frequency": 50.1,
            "ac_output_va": 345,
            "ac_output_w": 456,
            "output_load_percent": 90,
            "bus_voltage": 10,
            "battery_voltage": 34.56,
            "battery_charge_current": 13,
            "battery_capacity": 80,
            "inverter_temperature": 60,
            "pv_input_current": 10,
            "pv_input_voltage": 20.3,
            "scc_battery_voltage": 23.45,
            "battery_discharge_current": 12,
            "load_status": 0,
            "battery_voltage_steady": 0,
            "charging_on": 0,
            "scc_charging_on": 0,
            "ac_charging_on": 0,
            }
    }
    ]
    status_body[0]['fields']['grid_voltage'] = float(status_data[0])
    status_body[0]['fields']['grid_frequency'] = float(status_data[1])
    status_body[0]['fields']['ac_output_voltage'] = float(status_data[2])
    status_body[0]['fields']['ac_output_frequency'] = float(status_data[3])
    status_body[0]['fields']['ac_output_va'] = float(status_data[4])
    status_body[0]['fields']['ac_output_w'] = float(status_data[5])
    status_body[0]['fields']['output_load_percent'] = float(status_data[6])
    status_body[0]['fields']['bus_voltage'] = float(status_data[7])
    status_body[0]['fields']['battery_voltage'] = float(status_data[8])
    status_body[0]['fields']['battery_charge_current'] = float(status_data[9])
    status_body[0]['fields']['battery_capacity'] = float(status_data[10])
    status_body[0]['fields']['inverter_temperature'] = float(status_data[11])
    status_body[0]['fields']['pv_input_current'] = float(status_data[12])
    status_body[0]['fields']['pv_input_voltage'] = float(status_data[13])
    status_body[0]['fields']['scc_battery_voltage'] = float(status_data[14])
    status_body[0]['fields']['battery_discharge_current'] = float(status_data[15])
    the_bits = list(status_data[16])
    status_body[0]['fields']['load_status'] = int(the_bits[3])
    status_body[0]['fields']['battery_voltage_steady'] = int(the_bits[4])
    status_body[0]['fields']['charging_on'] = int(the_bits[5])
    status_body[0]['fields']['scc_charging_on'] = int(the_bits[6])
    status_body[0]['fields']['ac_charging_on'] = int(the_bits[7])
    client.write_points(status_body)


def populate_ratings_data(ratings_data, client):
    battery_type_dictionary = { '0': 'AGM', '1': 'Flooded', '2': 'User'}
    input_voltage_dictionary = { '0': 'Appliance', '1': 'UPS'}
    output_source_dictionary = { '0': 'Utility first', '1': 'Solar first', '2': 'SBU first'}
    charger_source_dictionary = { '0': 'Utility first', '1': 'Solar first', '2': 'Solar and utility', '3': 'Only solar'}
    machine_type_dictionary = { '00': 'Grid tie', '01': 'Off grid', '10': 'Hybrid'}
    topology_dictionary = { '0': 'Transformerless', '1': 'Transformer'}
    output_mode_dictionary = { '0': 'Single machine', '1': 'Parallel', '2': 'Phase 1 of 3', '3': 'Phase 2 of 3', '4': 'Phase 3 of 3'}
    ratings_body = [
    {
        "measurement": "system_rating",
        "tags": {
            "host": "test_installation1"
            },
        "fields": {
            "grid_voltage": 123.4,
            "grid_current": 50.0,
            "ac_output_voltage": 123.5,
            "ac_output_frequency": 50.1,
            "ac_output_current": 10.1,
            "ac_output_va": 345,
            "ac_output_w": 456,
            "battery_voltage": 34.56,
            "battery_recharge_voltage": 12.5,
            "battery_under_voltage": 13,
            "battery_bulk_voltage": 80,
            "battery_float_voltage": 60,
            "battery_type": "AGM",
            "max_ac_charge_current": 20,
            "max_charge_current": 23.45,
            "input_voltage_range": "Appliance",
            "output_source_priority": "SBU first",
            "charger_source_priority": "Utility first",
            "machine_type": "Grid tie",
            "topology": "Transformer",
            "output_mode": "Single machine",
            "battery_redischarge_voltage": 12.3,
            "pv_ok_for_parallel": 0,
            "pv_power_balance": 0, 
            }
    }
    ]
    ratings_body[0]['fields']['grid_voltage'] = float(ratings_data[0])
    ratings_body[0]['fields']['grid_current'] = float(ratings_data[1])
    ratings_body[0]['fields']['ac_output_voltage'] = float(ratings_data[2])
    ratings_body[0]['fields']['ac_output_frequency'] = float(ratings_data[3])
    ratings_body[0]['fields']['ac_output_current'] = float(ratings_data[4])
    ratings_body[0]['fields']['ac_output_va'] = float(ratings_data[5])
    ratings_body[0]['fields']['ac_output_w'] = float(ratings_data[6])
    ratings_body[0]['fields']['battery_voltage'] = float(ratings_data[7])
    ratings_body[0]['fields']['battery_recharge_voltage'] = float(ratings_data[8])
    ratings_body[0]['fields']['battery_under_voltage'] = float(ratings_data[9])
    ratings_body[0]['fields']['battery_bulk_voltage'] = float(ratings_data[10])
    ratings_body[0]['fields']['battery_float_voltage'] = float(ratings_data[11])
    ratings_body[0]['fields']['battery_type'] = battery_type_dictionary[ratings_data[12]]
    ratings_body[0]['fields']['max_ac_charge_current'] = float(status_data[13])
    ratings_body[0]['fields']['max_charge_current'] = float(ratings_data[14])
    ratings_body[0]['fields']['input_voltage_range'] = input_voltage_dictionary[ratings_data[15]]
    ratings_body[0]['fields']['output_source_priority'] = output_source_dictionary[ratings_data[16]]
    ratings_body[0]['fields']['charger_source_priority'] = charger_source_dictionary[ratings_data[17]]
    # Skip 18 (parallel max num)
    ratings_body[0]['fields']['machine_type'] = machine_type_dictionary[ratings_data[19]]
    ratings_body[0]['fields']['topology'] = topology_dictionary[ratings_data[20]]
    ratings_body[0]['fields']['output_mode'] = output_mode_dictionary[ratings_data[21]]
    ratings_body[0]['fields']['battery_redischarge_voltage'] = float(ratings_data[22])
    ratings_body[0]['fields']['pv_ok_for_parallel'] = float(ratings_data[23])
    ratings_body[0]['fields']['pv_power_balance'] = float(ratings_data[24])
    client.write_points(ratings_body)


def populate_data():
    global mode_data
    global status_data
    global influx_client
    try:
        if write_to_db:
            logger.info("Writing to database...")
            populate_mode_data(mode_data, influx_client)
            populate_status_data(status_data, influx_client)
            populate_ratings_data(ratings_data, influx_client)
    except Exception as e:
        logger.error(str(e))


# Read every 20 seconds =, write every 30
schedule.every(2).seconds.do(read_data)
schedule.every(3).seconds.do(populate_data)

logger.info("Program starts")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    main_window = MainWindow()
#    main_window.show()
#    sys.exit(app.exec_())

while True:
    schedule.run_pending()
    time.sleep(1)
