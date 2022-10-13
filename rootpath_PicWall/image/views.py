import datetime
import os
import re
import time
from django import forms
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import ImageForm
from .models import Image
# Create your views here.

@login_required
def list_images(request):
    """数据列表"""
    # 去数据库中获取所有数据
    images = Image.objects.filter(user=request.user)
    return render(request, 'image/list_images.html',{'images':images})

@login_required(login_url='/account/login/')
@csrf_exempt
@require_POST
def upload_image(request):
    form = ImageForm(data=request.POST)
    if form.is_valid():
        try:
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            return JsonResponse({'status':'1'})
        except:
            return JsonResponse({'status':'0'})



@login_required
def add_images(request):
    if request.method == "GET":
        form = ImageForm()
        return render(request, "image/image_add.html", {"form":form})
    form = ImageForm(data = request.POST)
    print("request.post: ",request.POST)
    if form.is_valid():
        form.save()
        return redirect("/image/list-images/")
    else:
        return render(request, "image/image_add.html",{'form':form})



def photo_add(request):
    """添加数据"""
    if request.method == "GET":
        return render(request, 'rootpath_photo_add.html')
    elif request.method == "POST":
        # 获取文本信息
        note = request.POST.get('note')
        print("note: ", note)
        # 获取数据
        file_list = request.FILES.getlist('file')
        for file_object in file_list:
            file_path = os.path.join(settings.MEDIA_ROOT, 'photos', file_object.name)
            # 将file_object保存到media/photos文件夹下
            print("file_path: ", file_path) # /home/dushiyi/my_web/rootpath_PicWall/meida/photos/1.jpg
            with open(file_path, 'wb') as f:
                for chunk in file_object.chunks():
                    f.write(chunk)
        
            # 提取图片的上传时间,上传人,图片名,图片路径,并保存到数据库
            photo_time = time.ctime(os.path.getctime(file_path))
            # 将time 转换为datetime类型
            photo_time = datetime.datetime.strptime(photo_time, "%a %b %d %H:%M:%S %Y")
            photo_name = file_object.name
            photo_path = "photos/" + file_object.name
            upload_time = datetime.datetime.now()
            owner = "admin"
            note = note
            # 打印出所有变量到同一行
            print("photo_name: ", photo_name, "photo_time: ", photo_time, "photo_path: ", photo_path, "upload_time: ", upload_time, "owner: ", owner, "note: ", note)
            # 将数据保存到数据库
            Image.objects.create(photo_name=photo_name, 
                                        photo_time=photo_time,
                                        photo_path=photo_path,
                                        upload_time=upload_time,
                                        owner=owner,
                                        note=note)
        # 获取数据库中photo_path的值,返回到photo_list.html页面
        queryset = Image.objects.all()
        return render(request, 'photo_list.html',{'queryset':queryset})

def photo_update(request):
    """
    去media_root目录下查询所有本地图片,得到一个列表
    1)看列表在不在mysql中,不在就添加到数据库表中.
    2)在mysql中查询列表,不在列表中就删除数据库中的数据.
    更新完后返回url(/photo/list/)
    """
    # 获取media/photos文件夹下的所有文件
    media_root = settings.MEDIA_ROOT
    # print("media_root: ", media_root)
    photos_path = os.path.join(media_root, 'photos')
    photos_list = os.listdir(photos_path) # ['1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.jpg', '10.jpg']
    # print("photos_list: ", photos_list)
    for each in photos_list:
        # 判断数据库中是否存在该数据
        if not Image.objects.filter(photo_path="photos/" + each).exists():
            # 将数据保存到数据库
            photo_time = time.ctime(os.path.getctime(photos_path+'/'+each))
            photo_time = datetime.datetime.strptime(photo_time, "%a %b %d %H:%M:%S %Y")
            photo_name = each
            photo_path = "photos/" + each
            upload_time = datetime.datetime.now()
            owner = "admin"
            note = "这是一张图片"
            # 更新到数据库中
            Image.objects.create(photo_name=photo_name,
                                        photo_time=photo_time,
                                        photo_path=photo_path,
                                        upload_time=upload_time,
                                        owner=owner,
                                        note=note)
    
    # 检查数据库表中的数据是否在本地，如果不在本地，也就是本地删除了图片，那么数据库中也删除该记录
    # 先查询数据库中的数据
    queryset = Image.objects.all() # <QuerySet [<Photo: Photo object (1)>, <Photo: Photo object (2)>, <Photo: Photo object (3)>]>
    # 循环查询数据库中的数据
    for each in queryset:
        # 判断数据库中的数据是否在本地
        # print("each.photo_path: ", each.photo_path)
        # print("photo_name: ", each.photo_name) # 1.jpg
        if each.photo_name not in photos_list:
            # 删除数据库中的数据
            each.delete()   
    return redirect('/photo/list/')

@login_required
@csrf_exempt
@require_POST
def del_image(request):
    """
    删除数据
    """
    image_id = request.POST['image_id']
    try:
        image = Image.objects.get(id=image_id)
        image.delete()
        return JsonResponse({'status':"1"})
    except:
        return JsonResponse({'status':'2'})

    # models.Image.objects.filter(id=nid).delete()
    # return redirect('/photo/list/')

def photo_scrolling(request):
    """
    图片滚动,old function
    """
    queryset = Image.objects.all()
    return render(request, 'photo_scrolling.html',{'queryset':queryset})


def falls_images(request):
    images = Image.objects.all()
    return render(request, 'image/falls_images.html', {'images':images})