# Python reader for solar panel controller

import evdev
from influxdb import InfluxDBClient
import schedule
import logging
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

def read_data():
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for device in devices:
        logging.info("{0} - {1} - {2} ".format(device.fn, device.name, device.phys))

def populate_data():
    logging.info("Writing to database...")

# Read every 10 seconds =, write every 20
schedule.every(20).seconds.do(read_data)
schedule.every(30).seconds.do(populate_data)

logging.info("Program starts")

while True:
    schedule.run_pending()
    time.sleep(1)
