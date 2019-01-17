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
    piri_file = open("qpigs.txt","r")
    mod_file = open("qmod.txt","r")

mode_data = []          # From QMOD command
status_data = []        # From QPIGS command
ratings_data = []       # From QPIRI command


# Read next line from each file, if at end of the file loop to the beginning
def read_file_data(input_file):
    return_data = []
    return_data = input_file.readline()
    if return_data is "":
        input_file.seek(0)
        return_data = input_file.readline()
    return return_data
    
# Setup logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

# Read data function (either from USB or file)
def read_data():
    global mode_data
    if debug_data:
        mode_data = read_file_data(mod_file)
        logging.info("Mode data: " + mode_data)
        status_data = read_file_data(piri_file)
        logging.info("Status data: " + status_data)
    else:
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
            logging.info("{0} - {1} - {2} ".format(device.fn, device.name, device.phys))

def populate_mode_data(mode_data, client):
    mode_dictionary = { 'P': 'Power on', 'S': 'Standby', 'L': 'Line',
                        'B': 'Battery', 'F': 'Fault', 'H': 'Power saving'}
    mode_body = {
        'measurement': 'system_mode',
        'tags': {
            'host': "test_installation1",
            },
        'fields': {
            'mode': 'unknown'
            }
    }
    if mode_data[0] in mode_dictionary.keys():
        mode_body['fields']['mode'] = mode_dictionary[mode_data[0]]
        client.write_points(mode_body)
    else:
        logging.error("Invalid mode {0}".format(mode_data[0]))

def populate_data():
    global mode_data
    global influx_client
    logging.info("Writing to database...")
    populate_mode_data(mode_data, influx_client)

# Read every 20 seconds =, write every 30
schedule.every(2).seconds.do(read_data)
schedule.every(5).seconds.do(populate_data)

logging.info("Program starts")

while True:
    schedule.run_pending()
    time.sleep(1)
