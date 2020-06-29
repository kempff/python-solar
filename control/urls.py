from django.urls import path

from .base_views import HomePageView
from .control_views import ControlView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('control', ControlView.as_view(), name='control'),
]
