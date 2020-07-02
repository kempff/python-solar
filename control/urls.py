from django.urls import path

from .home_views import HomePageView
from .control_views import ControlView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('control', ControlView.as_view(), name='control'),
]
