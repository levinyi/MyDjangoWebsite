from app01 import models
from django.shortcuts import render, HttpResponse, redirect
from app01.utils.pagination import Pagination
from app01.utils.form import UserModelForm


def user_list(request):
    """ 用户管理"""
    queryset = models.UserInfo.objects.all()
    page_object = Pagination(request, queryset, page_size=20)
    
    context = {  
        'queryset': page_object.page_queryset,  # 分完页的数据
        'page_string':page_object.html(),  # 页码
    }
    return render(request, 'user_list.html',context)


def user_add(request):
    """添加用户"""
    if request.method == "GET":
        content = {
            "gender_choices" : models.UserInfo.gender_choices,
            "depart_list": models.Department.objects.all(),
        }
        return render(request, "user_add.html", content)
    # 获取用户数据:
    name = request.POST.get("name")
    pwd = request.POST.get("pwd")
    age = request.POST.get("age")
    account = request.POST.get("account")
    ctime = request.POST.get("ctime")
    gender = request.POST.get("gender")
    depart_id = request.POST.get("depart_id")

    # 添加到数据库
    models.UserInfo.objects.create(name=name, password=pwd, account=account, 
                create_time=ctime, age=age,gender=gender,depart_id=depart_id)
    return redirect("/user/list/")

def user_model_form_add(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user_model_form_add.html", {"form":form})
    
    # POST提交的数据要校验:
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法,保存到数据库
        # print(form.cleaned_data)
        form.save()
        return redirect('/user/list/')
    else:
        # print(form.errors)
        return render(request, 'user_model_form_add.html', {'form':form})

def user_edit(request, nid):
    """编辑用户"""
    # 根据ID去数据库获取要编辑的那一行数据:
    row_object = models.UserInfo.objects.filter(id=nid).first()
    
    # 如果是GET请求:
    if request.method == "GET":
        # 还用之前的UserModelForm()
        form = UserModelForm(instance = row_object)
        return render(request, "user_edit.html",{"form":form})
    
    # 如果是POST请求:
    form = UserModelForm(data=request.POST, instance = row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据, 如果想要在用户输入以外增加一点值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/user/list/')
    return render(request, 'user_edit.html', {"form":form})


def user_delete(request, nid):
    """删除用户"""
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list/")

