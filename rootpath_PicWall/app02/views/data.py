import os
import json
import datetime
from logging import PlaceHolder
from pyexpat import model
from django import forms
# from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyrsistent import field
# from app01.utils.bootstrap import BootStrapModelForm
from app02 import models
from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ValidationError
from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapModelForm

def data_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    queryset = models.Data.objects.all().order_by("-id")
    # 获取data列表
    form = DataModelForm()
    # 用Pagination分页
    page_obj = Pagination(request, queryset)
    context = {
        'form':form,
        'queryset':page_obj.page_queryset,
        'page_string':page_obj.html()
    }
    return render(request, 'data_list.html', context)

from django import forms
class DataModelForm(BootStrapModelForm):
    # area = serializers.SerializerMethodField()
    class Meta:
        model = models.Data
        fields = ["data_path", "area"]

    # 校验数据是否存在
    def clean_data_path(self):
        txt_data_path = self.cleaned_data['data_path']
        print("txt_data_path: ",txt_data_path)
        exists = models.Data.objects.filter(data_path=txt_data_path).exists()
        if exists:
            raise ValidationError("路径已经存在")
        elif not txt_data_path.startswith("oss"):
            raise ValidationError("路径不符合要求：以oss://开头")
        elif not txt_data_path.endswith("Result"):
            raise ValidationError("路径不符合要求：以Result结尾")
        
        # get area choice value
        txt_area = self.data['area'] # 1,2,3
        area_choices = models.Data.area_choices
        # print("area_choices: ",area_choices) # (1, "华北"), (2, "华东"), (3, "华南")
        # find area choice value
        area_value = [area_choice[1] for area_choice in area_choices if area_choice[0] == int(txt_area)][0] # 华北/华东/华南...
        # print("txt_area: ",txt_area)
        # print("area_value: ",area_value)
        area_list = ["华北","华东","华中","华南"]
        
        dest_data_dir = os.path.basename(txt_data_path)[:4]
        print("dest_data_dir: ", dest_data_dir)

        # 保险起见，验证一下dest_data_dir是否是今年，如果不是，则抛出异常
        now_year = datetime.datetime.now().year
        print("now_year: ", now_year)
        if dest_data_dir != str(now_year):
            raise ValidationError("路径不符合要求：检测到不是以当年的年份开头，请联系管理员手动添加该数据")
        # 检查一下dest_data_dir是否存在,如果不存在，则创建
        if not os.path.exists('/cygene2/data/'+ dest_data_dir):
            os.makedirs('/cygene2/data/'+ dest_data_dir)

        if area_value not in area_list:
            raise ValidationError("区域不存在")
        elif area_value == "华北":
            endpoint = "oss-cn-beijing.aliyuncs.com"
            os.system('nohup /cygene/software/ossutil64 cp {}  /cygene2/data/{}/ -r -f --jobs 3 --parallel 10 --endpoint {} >/cygene2/data/{}/nohup.out 2>/cygene2/data/{}/nohup.err &'.format(txt_data_path, dest_data_dir, endpoint, dest_data_dir, dest_data_dir))
            print(    'nohup /cygene/software/ossutil64 cp {}  /cygene2/data/{}/ -r -f --jobs 3 --parallel 10 --endpoint {} >/cygene2/data/{}/nohup.out 2>/cygene2/data/{}/nohup.err &'.format(txt_data_path, dest_data_dir, endpoint, dest_data_dir, dest_data_dir))
        elif area_value == "华东":
            endpoint = "oss-cn-hangzhou.aliyuncs.com"
            os.system('nohup /cygene/software/ossutil64 cp {}  /cygene2/data/{}/ -r -f --jobs 3 --parallel 10 --endpoint {} >/cygene2/data/{}/nohup.out 2>/cygene2/data/{}/nohup.err &'.format(txt_data_path, dest_data_dir, endpoint, dest_data_dir, dest_data_dir))
            print(    'nohup /cygene/software/ossutil64 cp {}  /cygene2/data/{}/ -r -f --jobs 3 --parallel 10 --endpoint {} >/cygene2/data/{}/nohup.out 2>/cygene2/data/{}/nohup.err &'.format(txt_data_path, dest_data_dir, endpoint, dest_data_dir, dest_data_dir))
        else:
            endpoint = "oss-cn-hangzhou.aliyuncs.com"
            print('nohup /cygene/software/ossutil64 cp {}  /cygene2/data/{}/ -r -f --jobs 3 --parallel 10 --endpoint {} >/cygene2/data/{}/nohup.out 2>/cygene2/data/{}/nohup.err &'.format(txt_data_path, dest_data_dir, endpoint, dest_data_dir, dest_data_dir))
            raise ValidationError("目前还没有华南的数据哦,快去联系管理员验证一下吧！")
        return txt_data_path

@csrf_exempt
def data_add(request):
    """添加数据"""
    # 从ajax请求中获取的数据在request.post中就能得到
    print("request.POST:", request.POST)

    form = DataModelForm(data = request.POST)
    if form.is_valid():
        form.save()
        data_dict = {"status": True}
        return HttpResponse(json.dumps(data_dict))
    else:
        data_dict = {"status": False, "error": form.errors}
        return HttpResponse(json.dumps(data_dict, ensure_ascii=False))

def data_add_deprecated(request):
    """添加数据,用于前期学习,后期用ajax替代"""
    if request.method == "GET":
        form = DataModelForm()
        return render(request, "rootpath_data_add.html", {"form":form})
    form = DataModelForm(data = request.POST)

    if form.is_valid():
        form.save()
        return redirect("/data/list/")
    else:
        return render(request, "rootpath_data_add.html",{'form':form})


def data_edit(request, nid):
    """编辑数据"""
    # 根据ID去数据库获取要编辑的那一行数据:
    row_object = models.Data.objects.filter(id=nid).first()

    if request.method == "GET":
        form = DataModelForm(instance = row_object)
        return render(request, "rootpath_data_edit.html", {'form':form})
    # 如果是POST请求:
    form = DataModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/data/list/')
    return render(request, 'rootpath_data_edit.html',{'form':form})

def data_delete(request, nid):
    """删除数据"""
    models.Data.objects.filter(id=nid).delete()
    return redirect("/data/list/")


def data_update(request,):
    """
    去服务器查询所有数据,得到一个列表
    看列表在不在mysql中,不在就更新mysql,
    最后返回/data/list/
    """
    now_year = datetime.datetime.now().year
    data_list = os.listdir("/cygene2/data/"+str(now_year))
    for each in data_list:
        if each.startswith(str(now_year)) and each.endswith("Result"):
            data_path = "oss://novo-medical-customer-tj/X101SC20031639-Z03/" + each
            if not models.Data.objects.filter(data_path=data_path).exists():
                models.Data.objects.create(data_path=data_path, area=1)
    return redirect('/data/list/')