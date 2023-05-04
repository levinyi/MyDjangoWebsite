import datetime
import os

from django import forms
from django.core.exceptions import ValidationError

from . import models


class BootStrap:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget_attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label,
                }


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass


class DataModelForm(BootStrapModelForm):
    class Meta:
        model = models.Data
        fields = ["company", "area", "data_path", ]

    # 校验数据是否存在
    def clean_data_path(self):
        txt_data_path = self.cleaned_data['data_path']
        # print("txt_data_path: ", txt_data_path)
        exists = models.Data.objects.filter(data_path=txt_data_path).exists()
        if exists:
            raise ValidationError("路径已经存在")
        elif not txt_data_path.startswith("oss"):
            raise ValidationError("路径不符合要求：以oss://开头")

        # 保险起见，验证一下dest_data_dir是否是今年，如果不是，则抛出异常
        now_year = str(datetime.datetime.now().year)
        # print(now_year)
        # 检查一下dest_data_dir是否存在,如果不存在，则创建
        dest_data_dir = os.path.join('/cygene4/data/', now_year)
        if not os.path.exists(dest_data_dir):
            os.makedirs('/cygene4/data/' + now_year)

        # download from background.
        # 根据用户输入的area 从Endpoint数据库中获取 endpoint 
        area = self.cleaned_data['area']
        endpoint = models.EndPoint.objects.get(name=area).endpoint
        # print("endpoint: ", endpoint)

        # 根据用户选择的company 从CompanyInfo数据库中查询出 endpoint，keyID, keySecret
        company = self.cleaned_data['company']
        keyid = models.CompanyInfo.objects.get(name=company).KeyID
        keysecret = models.CompanyInfo.objects.get(name=company).KeySecret

        os.system('nohup /cygene/software/ossutil64 cp {} {} -r -f --jobs 3 --parallel 10 --access-key-secret {} --access-key-id {} --endpoint {} >{}/nohup.out 2>{}/nohup.err &'.format(
            txt_data_path, dest_data_dir, keysecret, keyid, endpoint, dest_data_dir, dest_data_dir))
        # print('nohup /cygene/software/ossutil64 cp {} {} -r -f --jobs 3 --parallel 10 --access-key-secret {} --access-key-id {} --endpoint {} >{}/nohup.out 2>{}/nohup.err &'.format(
        #        txt_data_path, dest_data_dir, keysecret, keyid, endpoint, dest_data_dir, dest_data_dir))
        return txt_data_path
