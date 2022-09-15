
from django.shortcuts import render, HttpResponse, redirect
from app01 import models


def depart_list(request):
    """部门列表"""
    # 1. 去数据库中获取所有的部门列表
    queryset = models.Department.objects.all()
    return render(request, 'depart_list.html', {"queryset":queryset})


def depart_add(request):
    """添加部门"""
    if request.method == "GET":
        return render(request, "depart_add.html")
    title = request.POST.get('title')
    # 保存到数据库
    models.Department.objects.create(title=title)
    return redirect("/depart/list/")


def depart_delete(request):
    """删除部门"""
    nid = request.GET.get("nid")
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/list/")


def depart_edit(request, nid):
    """修改部门信息"""
    if request.method == "GET":
        # 根据nid就能获取数据
        row_object = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {"row_object":row_object})
    title = request.POST.get('title')
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list/")
