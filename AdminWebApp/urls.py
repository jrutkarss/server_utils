from django.urls import path
from AdminWebApp import views 

urlpatterns = [
    path('',views.index,name='ls')
]