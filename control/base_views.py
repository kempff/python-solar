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

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import APP_NAME, APP_VERSION
from constants import SET_MAX_CURRENT, SET_AC_CURRENT, SET_BATTERY_REDISCHARGE_VOLTAGE 
from constants import SET_BATTERY_RECHARGE_VOLTAGE, SET_BATTERY_CUTOFF_VOLTAGE

the_logger = StructLogger()
the_logger.print_app_version()

# Configure ZMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
port = os.getenv('ZMQ_PORT', '5555')
socket.connect(f'tcp://localhost:{port}')

class HomePageView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        else:
            return render(request, "home.html")


