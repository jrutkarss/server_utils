from django.urls import path
from AdminWebApp import views 

urlpatterns = [
    path('',views.dashboard_home,name='dashboard_home')
]