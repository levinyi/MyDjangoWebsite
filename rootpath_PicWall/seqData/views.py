import datetime
import json
import os
import time

from django.shortcuts import HttpResponse, redirect, render
from django.views.decorators.csrf import csrf_exempt

from seqData import models

from .forms import DataModelForm
from .utils.pagination import Pagination


# Create your views here.
def data_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    queryset = models.Data.objects.all().order_by("-id")
    # # 获取data列表
    form = DataModelForm()
    # 用Pagination分页
    page_obj = Pagination(request, queryset)
    context = {
        'form':form,
        'queryset':page_obj.page_queryset,
        'page_string':page_obj.html()
    }
    return render(request, 'seqData/data_list.html', context)


def update(request):
    """
    去服务器查询所有数据,得到一个列表
    看列表在不在mysql中,不在就更新mysql,
    最后返回/data/list/
    """
    now_year = str(datetime.datetime.now().year)
    data_dir = "/cygene2/data/"
    data_list = os.listdir(os.path.join(data_dir, now_year))

    for each in data_list:
        if each.startswith(str(now_year)) and each.endswith("Result"):
            """NO的数据格式"""
            bucket_path = models.CompanyInfo.objects.get(name="诺和").bucket
            company = models.CompanyInfo.objects.get(name="诺和")
        elif each.startswith("GZCYYX"):
            """mm的数据格式"""
            bucket_path = models.CompanyInfo.objects.get(name="明码生物").bucket
            company = models.CompanyInfo.objects.get(name="明码生物")
        else:
            continue
        oss_path = os.path.join(bucket_path, each)
        true_path = os.path.join(data_dir, now_year, each)
        area = models.EndPoint.objects.get(id=2) #  "华北2(北京)"
        if not models.Data.objects.filter(data_path=oss_path).exists():
            ctime = time.strftime("%Y-%m-%d",time.localtime(os.path.getctime(true_path)))
            # print("{}\t{}\t{}\t{}".format(oss_path, true_path, ctime, company))
            models.Data.objects.create(data_path=oss_path, area=area, company=company, ctime=ctime)
    return redirect('/SeqData/data-list/')


@csrf_exempt
def data_add(request):
    """添加数据"""
    # 从ajax请求中获取的数据在request.post中就能得到
    # print("request.POST:", request.POST)

    form = DataModelForm(data = request.POST)
    if form.is_valid():
        form.save()
        data_dict = {"status": True}
        return HttpResponse(json.dumps(data_dict))
    else:
        data_dict = {"status": False, "error": form.errors}
        return HttpResponse(json.dumps(data_dict, ensure_ascii=False))


def data_delete(request, nid):
    """删除数据"""
    models.Data.objects.filter(id=nid).delete()
    return redirect("/SeqData/data-list/")


def data_edit(request, nid):
    """编辑数据"""
    row_object = models.Data.objects.filter(id=nid).first()

    if request.method == "GET":
        form = DataModelForm(instance = row_object)
        return render(request, "seqData/data_edit.html", {'form':form})
    # 如果是POST请求:
    form = DataModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/SeqData/data-list/')
    return render(request, 'seqData/data_edit.html',{'form':form})