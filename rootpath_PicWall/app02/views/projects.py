import os
from logging import PlaceHolder
from pyexpat import model
from django import forms
from django.shortcuts import render
from pyrsistent import field
# from app01.utils.bootstrap import BootStrapModelForm
from app02 import models
from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ValidationError


def project_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    # queryset = models.Data.objects.all()
    return render(request, 'project_list.html')

'''

from django import forms
class DataModelForm(forms.ModelForm):
    class Meta:
        model = models.Data
        fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs={
                "class":"form-control",
                'placeholder':field.label,
            }
    # 验证数据是否存在
    def clean_data_path(self):
        txt_data_path = self.cleaned_data['data_path']
        exists = models.Data.objects.filter(data_path=txt_data_path).exists()
        if exists:
            raise ValidationError("路径已经存在")
        else:
            # download to server.
            os.system('nohup /cygene/software/ossutil64 cp {}  /cygene2/data/2022/ -r -f --jobs 3 --parallel 10 --endpoint oss-cn-beijing.aliyuncs.com >/cygene2/data/2022/nohup.out 2>/cygene2/data/2022/nohup.err &'.format(txt_data_path))
        return txt_data_path

def data_add(request):
    """添加数据"""
    if request.method == "GET":
        form = DataModelForm()
        return render(request, "rootpath_data_add.html", {"form":form})
    form = DataModelForm(data = request.POST)
    # print(form)

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


'''


