# Load external modules
import structlog
import logging
import sys
import os
import math
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.generic.base import View
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
import zmq
import json
from influxdb import InfluxDBClient

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import APP_NAME, APP_VERSION, DATABASES
from constants import SET_MAX_CURRENT, SET_AC_CURRENT, SET_BATTERY_REDISCHARGE_VOLTAGE 
from constants import SET_BATTERY_RECHARGE_VOLTAGE, SET_BATTERY_CUTOFF_VOLTAGE

the_logger = StructLogger()
the_logger.print_app_version()

# Configure ZMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
port = os.getenv('ZMQ_PORT', '5555')
socket.connect(f'tcp://localhost:{port}')

class InfluxInterface:

    def __init__(self):
        # Configure DB
        self.influx_client = InfluxDBClient(DATABASES['influx']['INFLUX_HOST'], DATABASES['influx']['INFLUX_PORT'], 
                database=DATABASES['influx']['INFLUX_DB'])
        the_logger.info(f"Influx client: {self.influx_client}")


    def get_measurement_data(self):
        '''
        Performs the queries and return the result from InfluxDB
        '''
        solar_data = {
                "battery_percentage": 70,
                "ac_power": {
                    "current": 120,
                    "24hours": 15000,
                },
                "pv_power": {
                    "current": 220,
                    "24hours": 10000,
                }
            }
        return solar_data

# Create the InfluxDB interface object
influx_interface = InfluxInterface()

class HomePageView(View):
    global influx_interface

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            solar_data = influx_interface.get_measurement_data()
            return render(request, "home.html", {'solar_data':solar_data})
