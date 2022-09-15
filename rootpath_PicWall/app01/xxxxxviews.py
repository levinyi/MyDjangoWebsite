# -- coding: utf-8 --
import imp
from pyexpat import model
from re import A, U
from stat import FILE_ATTRIBUTE_NORMAL
from tkinter import N
from tokenize import endpats
from unicodedata import name
from xml.dom import ValidationErr
from xml.sax import default_parser_list
from attr import fields
from django.shortcuts import render, HttpResponse, redirect
from grpc import Status
from requests import request
from sklearn.exceptions import DataDimensionalityWarning

from django.utils.html import mark_safe

# Create your views here.
# def index(request):
#     return HttpResponse("Hello World!")

def index(request):
    # 1.优先去项目根目录的templates中寻找
    #    根目录下需要创建templates目录,且setting中还要配置TEMPLATES-->'DIRS':[os.path.join(BASE_DIR,'templates')]
    # 2.根据app的注册顺序，在每个app下的templates目录中寻找
    return render(request,'index.html')

def news(req):
    import requests
    import json
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en,en-GB;q=0.9,zh-TW;q=0.8,zh;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "text/plain;charset=UTF-8",
        "Cookie": "_dd_s=logs=1&id=0db82dd4-cc7c-4ece-8eed-93f70f93f6a9&created=1650427284747&expire=1650428357288",
        "DNT": "1",
        "Host": "www.chinaunicom.com.cn",
        "Referer": "http://www.chinaunicom.com.cn/news/list202204.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        }
    res = requests.get("http://www.chinaunicom.com.cn/api/article/NewsByIndex/3/2022/04/news",headers=headers)
    #print(res.content)
    #print(res.raw)
    #print(res.text)
    data_list = json.loads(res.text)
    return render(req, 'news.html',{'data_list':data_list})


from app01.models import UserInfo
def login(req):
    if req.method == "GET":
        return render(req,"login.html")
    
    # print(req.POST)
    username = req.POST.get("user")
    password = req.POST.get("pwd")
        
    """
        if username == "root" and password == "123":
        # return HttpResponse("success")
        return redirect("www.baidu.com")
    return render(req, "login.html", {"error_msg":"error user name or password"})
    """
    ####### 1.新建 #########
    UserInfo.objects.create(name = username, password = password)

    ####### 2.删除 #########
    # UserInfo.objects.filter(name = username).delete()
    # UserInfo.objects.all().delete()

    ####### 3.获取数据 #######
    # 3.1 获取符合条件的数据
    # data_list = [对象,对象,对象] QuerySet 类型,
    # data_list = UserInfo.objects.all()
    # for obj in data_list:
    #     print(obj.id, obj.name, obj.password, obj.age)

    # data_list = [对象,]
    # data_list = UserInfo.objects.filter(id=1)
    # print(data_list)
    # # 3.2 获取第一条数据[对象]
    # row_obj = UserInfo.objects.filter(id=1).first()
    # print(row_obj.id, row_obj.name,row_obj.password, row_obj.age)

    ####### 4.更新数据 #######
    # UserInfo.objects.all().update(password=999)
    # UserInfo.objects.filter(name="root").update(password="sdf")
    # return HttpResponse("已导入到数据库中!")
    return redirect('/info/list/')


def info_list(request):
    data_list = UserInfo.objects.all()
    return render(request, "info_list.html", {"data_list":data_list})


def info_delete(request):
    nid = request.GET.get('nid')
    UserInfo.objects.filter(id=nid).delete()
    return redirect("/info/list/")

