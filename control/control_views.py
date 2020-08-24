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
import time

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import APP_NAME, APP_VERSION
from constants import SET_MAX_CURRENT, SET_AC_CURRENT, SET_BATTERY_REDISCHARGE_VOLTAGE 
from constants import SET_BATTERY_RECHARGE_VOLTAGE, SET_BATTERY_CUTOFF_VOLTAGE
from control.influx_interface import InfluxInterface

the_logger = StructLogger()
influx_interface = InfluxInterface()


# Configure ZMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
port = os.getenv('ZMQ_PORT', '5555')
socket.connect(f'tcp://localhost:{port}')

class ControlView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            solar_data = influx_interface.get_ratings_data()
            return_val = {
                'command_result': None,
                'ratings': solar_data,
            }
            return render(request, "control.html", {'solar_data': return_val})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            command = None
            data = None
            return_val = None
            commands = {
                'max_charge_current_btn' : {'value':'max_charge_current_val','command':SET_MAX_CURRENT},
                'ac_charge_current_btn' : {'value':'ac_charge_current_val','command':SET_AC_CURRENT},
                'battery_redischarge_voltage_btn' : {'value':'battery_redischarge_voltage_val','command':SET_BATTERY_REDISCHARGE_VOLTAGE},
                'battery_recharge_voltage_btn' : {'value':'battery_recharge_voltage_val','command':SET_BATTERY_RECHARGE_VOLTAGE},
                'battery_cutoff_voltage_btn' : {'value':'battery_cutoff_voltage_val','command':SET_BATTERY_CUTOFF_VOLTAGE},
            }
            for key in commands.keys():
                if self.request.POST.get(key):
                    data = self.request.POST.get(commands[key]['value'])
                    command = commands[key]['command']
                    the_logger.info(f"{key}: {data} ({command})")
                    break                
            # If there is a command, send it via ZMQ
            if command:
                data = dict(command=command,data=data)
                try:
                    socket.send_json(data)
                    if socket.poll(1000, zmq.POLLIN):
                        message = socket.recv().decode('utf8')
                        command_data = json.loads(message)
                        the_logger.info(f"Reply: {command_data}")
                        time.sleep(2)
                        solar_data = influx_interface.get_ratings_data()
                        return_val = {
                            'command_result': command_data,
                            'ratings': solar_data,
                        }
                        the_logger.info(f"Ratings reply: {return_val}")
                    else:
                        the_logger.warning("error: message timeout")
                except Exception as e:
                    the_logger.error(f'ZMQ error: {str(e)}')
            return render(request, "control.html", {'solar_data': return_val})

