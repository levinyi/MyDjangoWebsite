from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('tools-list/', views.tools_list, name='tools_list'),
    path('tools-use/<str:tools_name>/', views.tools_use, name='tools_use'),
    path('check_status/<str:tools_name>/', views.check_status, name='check_status'),
    path('download_result/<str:unique_id>/', views.download_result, name='download_result'),
    path('delete_result/<str:tools_name>/<str:unique_id>/', views.delete_result, name='delete_result'),
    path('write_data_to_feishu_Sheet/', views.write_data_to_feishu_Sheet, name='write_data_to_feishu_Sheet'),
    path('plate_view/', views.plate_view, name='plate_view'),

    path('inquiry_create/', views.inquiry_create, name='inquiry_create'),
    path('inquiry_list/', views.inquiry_list, name='inquiry_list'),
    path('inquiry_delete/<int:pk>/', views.inquiry_delete, name='inquiry_delete'),
    path('inquiry_detail/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiry_validation/<int:pk>/', views.inquiry_validation, name='inquiry_validation'),
    path('inquiry_save/<int:pk>/', views.inquiry_save, name='inquiry_save'),
    path('inquiry_download/<int:pk>/', views.inquiry_download, name='inquiry_download'),

    
    path('test/', views.test, name='test'),
]