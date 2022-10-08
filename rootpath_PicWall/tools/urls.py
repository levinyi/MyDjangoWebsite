from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('tools-list', views.tools_list, name="tools_list"),
    path('<str:tool_name>/', views.tools_use, name='tools_use'),

]