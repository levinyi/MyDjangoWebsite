from django.urls import path
from . import views

app_name = 'image'

urlpatterns = [
    path('list-images/', views.list_images, name="list_images"),
    path('upload-image', views.upload_image, name='upload_image'),
    path('del-image/', views.del_image, name='del_image'),
    path('images/', views.falls_images, name='falls_images'),
    
    path('add/', views.photo_add, name="photo_add"),
    path('update/', views.photo_update, name="photo_update"),
    path('scrolling/', views.photo_scrolling, name="photo_scrolling"),
]