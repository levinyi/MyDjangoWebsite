import imp
from requests import request
from app01 import models
from django.shortcuts import render, HttpResponse, redirect
from app01.utils.pagination import Pagination

from app01.utils.form import PrettyModelForm,PrettyEditModelForm

def pretty_list(request):
    """靓号列表"""

    data_dict = {}
    search_data = request.GET.get('q','')
    if search_data:
        data_dict['mobile__contains'] = search_data
    # res = models.PrettyNum.objects.filter(**data_dict)
    # for i in range(300):
    #     models.PrettyNum.objects.create(mobile=random.randint(13000000000,19999999999),price=10,level=1,status=1)
    # 1. 根据用户想要访问的页码,计算出起止位置

    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level")

    page_object = Pagination(request, queryset)
    
    context = {
        'search_data':search_data,  
        'queryset': page_object.page_queryset,  # 分完页的数据
        'page_string':page_object.html(),  # 页码
    }

    return render(request, 'pretty_list.html', context)


def pretty_add(request):
    if request.method == "GET":
        form = PrettyModelForm()
        return render(request, "pretty_add.html",{"form":form})
    form = PrettyModelForm(data=request.POST)

    if form.is_valid():
        form.save()
        return redirect('/number/list/')
    else:
        # print(form.errors) at html.
        return render(request, 'pretty_add.html', {'form':form})



def pretty_edit(request, nid):
    """编辑靓号"""
    # 根据ID去数据库获取要编辑的那一行数据:
    row_object = models.PrettyNum.objects.filter(id=nid).first()
    
    # 如果是GET请求:
    if request.method == "GET":
        # 如果要跟之前添加页面一致,就还用之前的PrettyModelForm()
        # 如果想要不一致,比如我固定不能编辑电话,就要重新写一个PrettyEditModelForm()
        form = PrettyEditModelForm(instance = row_object)
        return render(request, "pretty_edit.html",{"form":form})
    
    # 如果是POST请求:
    form = PrettyEditModelForm(data=request.POST, instance = row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据, 如果想要在用户输入以外增加一点值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/number/list/')
    return render(request, 'pretty_edit.html', {"form":form})


def pretty_delete(request, nid):
    """删除用户"""
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect("/number/list/")
