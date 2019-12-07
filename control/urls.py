from django.urls import path

from .base_views import HomePageView


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]
