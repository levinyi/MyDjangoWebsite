from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'tools'

urlpatterns = [
    path('tools-list/', views.tools_list, name='tools_list'),
    path('<str:tools_name>/', views.tools_use, name='tools_use'),
]