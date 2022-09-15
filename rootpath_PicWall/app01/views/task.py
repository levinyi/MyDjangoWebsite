import json
from attr import fields
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01.utils.bootstrap import BootStrapModelForm
from app01.utils.pagination import Pagination
from app01 import models

class TaskModelForm(BootStrapModelForm):
    class Meta:
        model = models.Task
        fields = "__all__"

        
def task_list(request):
    """ 任务列表 """
    # 1. 获取所有的任务信息
    queryset = models.Task.objects.all().order_by("-id")

    # 1. 获取任务列表
    form = TaskModelForm()
    # 2. 分页
    page_object = Pagination(request, queryset)
    # 3. 渲染模板
    context = {
        "form": form,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html()
    }
    return render(request, 'task_list.html', context)


@csrf_exempt
def task_ajax(request):
    """ 任务列表 """
    print("request.GET: ", request.GET)
    print("request.POST: ", request.POST)

    data_dict = {"status": True, "msg": "ok", "data": ["11","22","33"]}
    # return HttpResponse(json.dumps(data_dict))
    return JsonResponse(data_dict)

@csrf_exempt
def task_add(request):
    """ 添加任务 """
    print("request.POST: ", request.POST)

    # 1.用户发送过来的数据进行校验
    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        # 2. 校验成功，保存数据
        form.save()
        # 3. 返回结果
        data_dict = {"status": True}
        return HttpResponse(json.dumps(data_dict))
    else:
        # 4. 校验失败，返回错误信息
        data_dict = {"status": False, "error": form.errors}
        return HttpResponse(json.dumps(data_dict, ensure_ascii=False))