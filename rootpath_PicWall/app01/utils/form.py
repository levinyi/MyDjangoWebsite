from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


from app01.utils.bootstrap import BootStrapForm, BootStrapModelForm
from app01.utils.encrypt import md5
from app01 import models


class UserModelForm(BootStrapModelForm):
    # 用户的验证规则有很多:比如密码必须大于6:
    password = forms.CharField(min_length=6, label="密码")
    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'age','account','gender','create_time','depart']

class PrettyModelForm(BootStrapModelForm):
    # # mobile 要校验数字长短,
    # 验证方式一:
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误,必须是1开头3-9第二位,后面任意')],
    )

    class Meta:
        model = models.PrettyNum
        # fields = "__all__"
        # exclude = ['level']
        fields = ['mobile', 'price', 'level', 'status']
    
    # # 没有格式,就要加这些:
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     for name, field in self.fields.items():
    #         field.widget.attrs = {"class": 'form-control','placeholder': field.label}
    # 验证方式2:
    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")
        return txt_mobile

class PrettyEditModelForm(BootStrapModelForm):
    # 如果不允许修改mobile,就可以重写mobile
    # mobile = forms.CharField(disabled=True, label="手机号")
    class Meta:
        model = models.PrettyNum
        fields = ['mobile','price', 'level', 'status']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     for name, field in self.fields.items():
    #         # 如果不想显示,就可以if 过滤掉.
    #         # if name == "password":
    #         #     continue
    #         field.widget.attrs = {
    #             "class": "form-control",
    #             "placeholder":field.label,
    #         }
    # 验证方式2:
    def clean_mobile(self):
        # 当前编辑的行的id
        # print(self.instance.pk)

        txt_mobile = self.cleaned_data["mobile"]
        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已存在")
        return txt_mobile


class AdminModelForm(BootStrapModelForm):

    confirm_password = forms.CharField(label="确认密码", widget=forms.PasswordInput(render_value=True))
    class Meta:
        model = models.Admin
        fields = ['admin_name', 'admin_pwd', 'confirm_password']
        widgets = {
            'admin_pwd': forms.PasswordInput(render_value=True),
        }

    def clean_admin_pwd(self):
        admin_pwd = self.cleaned_data.get("admin_pwd")
        return md5(admin_pwd)
    
    def clean_confirm_password(self):
        print(self.cleaned_data)
        admin_pwd = self.cleaned_data.get("admin_pwd")
        confirm_password = md5(self.cleaned_data.get("confirm_password"))
        print(admin_pwd, confirm_password)

        print(self.cleaned_data)
        if admin_pwd != confirm_password:
            self.add_error("admin_pwd", "两次密码不一致")
        return confirm_password


class LoginForm(BootStrapForm):
    admin_name = forms.CharField(
        label="用户名", 
        max_length=64, 
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入用户名"})
        )
    admin_pwd = forms.CharField(
        label="密码", 
        max_length=64,
        required=True, 
        widget=forms.PasswordInput(render_value=True),
        )
    code = forms.CharField(
        label="验证码",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入验证码"})
        )
    def clean_admin_pwd(self):
        admin_pwd = self.cleaned_data.get("admin_pwd")
        return md5(admin_pwd)


class LoginModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin
        fields = ['admin_name', 'admin_pwd']
    def clean_admin_pwd(self):
        admin_pwd = self.cleaned_data.get("admin_pwd")
        return md5(admin_pwd)