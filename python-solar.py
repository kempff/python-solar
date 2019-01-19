# Python reader for solar panel controller

import evdev
from influxdb import InfluxDBClient
import schedule
import logging
import time

influx_client = InfluxDBClient('localhost', 8086, database='solardb')

debug_data = True
if debug_data:
    # Open the files for reading
    pigs_file = open("qpigs.txt","r")
    mod_file = open("qmod.txt","r")

mode_data = []          # From QMOD command
status_data = []        # From QPIGS command
ratings_data = []       # From QPIRI command

# Setup logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)


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
    if debug_data:
        mode_data = read_file_data(mod_file).split()
        logging.info("Mode data: {0}".format(mode_data))
        status_data = read_file_data(pigs_file).split()
        logging.info("Status data: {0}".format(status_data))
    else:
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
            logging.info("{0} - {1} - {2} ".format(device.fn, device.name, device.phys))



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
        logging.error("Invalid mode {0}".format(mode_data[0]))
    
        
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
    logging.info(status_data)
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


def populate_data():
    global mode_data
    global status_data
    global influx_client
    logging.info("Writing to database...")
    populate_mode_data(mode_data, influx_client)
    populate_status_data(status_data, influx_client)


# Read every 20 seconds =, write every 30
schedule.every(2).seconds.do(read_data)
schedule.every(3).seconds.do(populate_data)

logging.info("Program starts")

while True:
    schedule.run_pending()
    time.sleep(1)
