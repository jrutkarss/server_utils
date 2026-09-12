
from django.urls import path
from MainWebApp import views

urlpatterns = [
    path('',views.index,name='home'),
    path('ingest/', views.ingest_telemetry, name='ingest_telemetry')
    ]