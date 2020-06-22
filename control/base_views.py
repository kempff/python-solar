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

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import APP_NAME, APP_VERSION
from constants import SET_MAX_CURRENT, SET_AC_CURRENT

the_logger = StructLogger()
the_logger.print_app_version()

pv_charge_current = None
ac_charge_current = None
battery_recharge_v = None
battery_re_discharge_v = None

# Configure ZMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
port = os.getenv('ZMQ_PORT', '5555')
socket.connect(f'tcp://localhost:{port}')

class HomePageView(View):
    global pv_charge_current
    global ac_charge_current
    global battery_recharge_v
    global battery_re_discharge_v
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            return render(request, "home.html")

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            if self.request.POST.get('max_charge_current_btn'):
                pv_charge_current = self.request.POST.get('max_charge_current_val')
                the_logger.info(f"Max charge current: {pv_charge_current}")
                data = dict(command=SET_MAX_CURRENT,data=pv_charge_current)
                socket.send_json(data)
                if socket.poll(1000, zmq.POLLIN):
                    message = socket.recv()
                    the_logger.info(f"Reply: {message}")
                else:
                    the_logger.warning("error: message timeout")
            if self.request.POST.get('ac_charge_current_btn'):
                ac_charge_current = self.request.POST.get('ac_charge_current_val')
                the_logger.info(f"AC charge current: {ac_charge_current}")
                # send_command(SET_AC_CURRENT,ac_charge_current).delay()
            battery_recharge_v = self.request.POST.get('battery_recharge_v')
            battery_re_discharge_v = self.request.POST.get('battery_re_discharge_v')
            return render(request, "home.html")

