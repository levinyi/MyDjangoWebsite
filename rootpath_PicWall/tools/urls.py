from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('tools-list/', views.tools_list, name='tools_list'),
    path('tools-use/<str:tools_name>/', views.tools_use, name='tools_use'),
    path('check-status/', views.check_status, name='check_status'),
    path('download_result/<str:unique_id>', views.download_result, name='download_result'),
]