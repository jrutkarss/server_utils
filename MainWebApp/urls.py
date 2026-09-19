
from django.urls import path
from MainWebApp import views

urlpatterns = [
    path('', views.index, name='home'),
    path('ingest/', views.ingest_telemetry, name='ingest_telemetry'),
    path('network-devices/discover/', views.discover_network_devices, name='discover_devices'),
    path('network-devices/metrics/', views.ingest_network_metrics, name='ingest_network_metrics'),
    path('network-devices/', views.get_network_devices, name='get_network_devices'),
]