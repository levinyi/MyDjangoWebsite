"""rootpath_PicWall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin as adm
from django.urls import path
from django.conf.urls.static import static
from app01.views import account,depart,pretty,user, admin, task
from app02.views import data, photo, tools, projects

urlpatterns = [
    path('admin/', adm.site.urls),
    # path('index/', views.index),
    # path('news/',  views.news),
    path('login/', account.login),
    path('logout/', account.logout),
    path('image/code/', account.image_code),
    # path('info/list/', views.info_list),
    # path('info/delete/', views.info_delete),
    ###### 部门管理
    path('depart/list/', depart.depart_list),
    path('depart/add/',    depart.depart_add),
    path('depart/<int:nid>/edit/',depart.depart_edit),
    path('depart/delete/', depart.depart_delete),
    ###### 用户管理
    path('user/list/',user.user_list),
    path('user/add/', user.user_add),
    path('user/model/form/add/', user.user_model_form_add),
    path('user/<int:nid>/edit/', user.user_edit),
    path('user/<int:nid>/delete/', user.user_delete),

    ##### 靓号管理
    path('number/list/', pretty.pretty_list),
    path('number/add/', pretty.pretty_add),
    path('number/<int:nid>/edit/', pretty.pretty_edit),
    path('number/<int:nid>/delete/', pretty.pretty_delete),

    ##### 管理员管理
    path('admin/list/', admin.admin_list),
    path('admin/add/', admin.admin_add),
    path('admin/<int:nid>/edit/', admin.admin_edit),
    path('admin/<int:nid>/delete/', admin.admin_delete),
    path('admin/<int:nid>/reset/', admin.admin_reset),

    ##### 任务管理，测试Ajax
    path('task/list/', task.task_list),
    path('task/ajax/', task.task_ajax),
    path('task/add/', task.task_add),


    ##### app02 数据管理
    path('data/list/', data.data_list),
    path('data/add/', data.data_add),
    path('data/update/', data.data_update),
    path('data/<int:nid>/delete/', data.data_delete),
    path('data/<int:nid>/edit/', data.data_edit),


    ##### app02 照片管理
    path('photo/list/', photo.photo_list),
    path('photo/add/', photo.photo_add),
    path('photo/update/', photo.photo_update),
    path('photo/<int:nid>/delete/', photo.photo_delete),
    path('photo/scrolling/', photo.photo_scrolling),
    
    ##### app02 项目管理
    path('project/list/', projects.project_list),


    ##### app02 小工具
    path('tools/list/', tools.tools_list),
    path('tools/<str:tools_name>/use/', tools.tools_use),
    path('tools/<str:tools_name>/update/', tools.tools_update),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


