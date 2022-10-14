from django.urls import path
from . import views

app_name = 'seqData'

urlpatterns = [
    path('data-list/', views.data_list, name='data_list'),
    path('update/', views.update, name='update'),
    path('add/', views.data_add, name="add"),
    path('delete/<int:nid>/', views.data_delete, name="data_delete"),
    path('edit/<int:nid>/', views.data_edit, name="data_edit"),
    # path('tools-use/<str:tools_name>/', views.tools_use, name='tools_use'),
]