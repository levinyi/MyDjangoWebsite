import imp
from django.shortcuts import redirect, render
from matplotlib.pyplot import title

from app01 import models
# 导入utils中的pagination组件
from app01.utils.pagination import Pagination
from app01.utils.encrypt import md5
from app01.utils.form import AdminModelForm

def admin_list(request):
    """
    管理员列表
    :param request:
    :return:
    """
    info_dict = request.session["info"]
    print("info_dict: ", info_dict)

    # 搜索
    data_dict = {}
    search_data = request.GET.get("q", "")
    if search_data:
        data_dict["admin_name__contains"] = search_data
    
    # 分页
    queryset = models.Admin.objects.filter(**data_dict).order_by("-id")
    # 实例化分页对象
    page_object = Pagination(request, queryset)
    context = {
        'queryset': queryset,  
        'page_string': page_object.html(),  # 页码
        'search_data': search_data,
    }
    return render(request, 'admin_list.html', context)


def admin_add(request):
    """
    添加管理员
    :param request:
    :return:
    """
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, 'change.html', {"title": "添加管理员", "form": form})

    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        # print(form.cleaned_data) # {'admin_name': 'admin', 'admin_pwd': '123456', 'confirm_password': '123456'}
        form.save()
        return redirect('/admin/list/')

    return render(request, 'change.html', {"title": "添加管理员", "form": form, "error": form.errors})  # 如果验证失败，则返回错误信息


def admin_edit(request, nid):
    """
    编辑管理员
    :param request:
    :param nid:
    :return:
    """
    obj = models.Admin.objects.filter(id=nid).first()
    if not obj:
        return redirect('/admin/list/')
    if request.method == "GET":
        form = AdminModelForm(instance=obj)
        return render(request, 'change.html', {"title": "编辑管理员", "form": form})

    form = AdminModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')
    return render(request, 'change.html', {"title": "编辑管理员", "form": form, "error": form.errors})  # 如果验证失败，则返回错误信息


def admin_delete(request, nid):
    """
    删除管理员
    :param request:
    :param nid:
    :return:
    """
    obj = models.Admin.objects.filter(id=nid).first()
    if not obj:
        return redirect('/admin/list/')
    obj.delete()
    return redirect('/admin/list/')


def admin_reset(request, nid):
    """
    重置管理员密码
    :param request:
    :param nid:
    :return:
    """
    obj = models.Admin.objects.filter(id=nid).first()
    if not obj:
        return redirect('/admin/list/')
    
    title = "重置管理员密码 - {}".format(obj.admin_name)
    return render(request, 'change.html', {"title": title, "form": AdminModelForm(instance=obj)})