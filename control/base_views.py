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

# Load internal modules
from solar.struct_logger import StructLogger
from solar.settings import APP_NAME, APP_VERSION

the_logger = StructLogger()
the_logger.info(f'Running {APP_NAME} version {APP_VERSION}')

pv_charge_current = None
ac_charge_current = None
battery_recharge_v = None
battery_re_discharge_v = None


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
            pv_charge_current = self.request.POST.get('pv_charge_current')
            ac_charge_current = self.request.POST.get('ac_charge_current')
            battery_recharge_v = self.request.POST.get('battery_recharge_v')
            battery_re_discharge_v = self.request.POST.get('battery_re_discharge_v')
            return render(request, "home.html")

