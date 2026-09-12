
from django.urls import path
from MainWebApp import views

urlpatterns = [
    path('',views.index,name='home')
    ]