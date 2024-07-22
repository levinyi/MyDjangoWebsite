import datetime
import os

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from . import models
from .tasks import download_data_from_oss_path, download_data_from_tos_path
from project_management.project_scripts.feishu import get_access_token
from decouple import config

app_id = config('FEISHU_APP_ID')
app_secret = config('FEISHU_APP_SECRET')

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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # 安全地弹出user，避免KeyError
        super().__init__(*args, **kwargs)
    
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
        elif not txt_data_path.startswith(("oss://","tos://")):
            raise ValidationError("路径不符合要求：以oss://开头,或者以tos://开头")

        now_year = str(datetime.datetime.now().year)
        # 检查一下dest_data_dir是否存在,如果不存在，则创建
        dest_data_dir = os.path.join('/cygene4/data/', now_year)
        if not os.path.exists(dest_data_dir):
            os.makedirs('/cygene4/data/' + now_year)

        # 将数据库查询移到表单提交后执行
        self.fetch_endpoint_and_company_info()

        return txt_data_path
    
    def fetch_endpoint_and_company_info(self):
        # 根据用户输入的area 从Endpoint数据库中获取 endpoint 
        area = self.cleaned_data['area']
        endpoint = models.EndPoint.objects.get(name=area).endpoint
        # print("endpoint: ", endpoint)

        # 根据用户选择的company 从CompanyInfo数据库中查询出 endpoint，keyID, keySecret
        company = self.cleaned_data['company']
        keyid = models.CompanyInfo.objects.get(name=company).KeyID
        keysecret = models.CompanyInfo.objects.get(name=company).KeySecret

        access_token = get_access_token(app_id, app_secret)
        
        # 获取用户的email
        if self.user.is_authenticated:
            email = self.user.email
        else:
            raise ValidationError("用户未登录")
        # print("company: ", company)
        if "火山引擎" in str(company):
            # print("yes, I am here")
            download_data_from_tos_path.delay(self.cleaned_data['data_path'], os.path.join('/cygene4/data/', str(datetime.datetime.now().year)), access_token, email)
        else:
            download_data_from_oss_path.delay(self.cleaned_data['data_path'], os.path.join('/cygene4/data/', str(datetime.datetime.now().year)), keysecret, keyid, endpoint, access_token, email)
