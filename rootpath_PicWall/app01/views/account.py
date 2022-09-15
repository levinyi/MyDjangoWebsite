import imp
from django.http import HttpResponse
from django.shortcuts import render, redirect
from app01.utils.pagination import Pagination
from app01.utils.bootstrap import BootStrapModelForm
from app01 import models
# 从utils中导入loginModelForm组件
from app01.utils.form import LoginModelForm, LoginForm
from app01.utils.code import check_code
from io import BytesIO # 内存中读取图片




def login(request):
    """
    登录页面
    :param request:
    :return:
    """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"title": "登录", "form": form})
    
    form = LoginForm(data=request.POST)
    if form.is_valid():
        print("form.cleaned_data: ", form.cleaned_data)
        # 验证码的校验
        user_input_code = form.cleaned_data.pop("code")
        session_code = request.session.get("code_str")
        if user_input_code.lower() != session_code.lower():
            form.add_error("code", "验证码错误")
            return render(request, 'login.html', {"form": form})

        print("form.cleaned_data: ", form.cleaned_data)
        # 去数据库中检验用户名和密码是否正确
        user = models.Admin.objects.filter(**form.cleaned_data).first()
        # print("user: ", user) # <app01.models.Admin: Admin object (1)>
        if not user:
            form.add_error("admin_name", "用户名或密码错误")
            return render(request, 'login.html', {"title": "登录", "form": form})
        else:
            # 登录成功
            # 将用户名存入session
            request.session["info"] = {'id': user.id, 'admin_name':user.admin_name}
            # session重新设置过期时间
            request.session.set_expiry(60*60*24*7) # 7天
            return redirect("/admin/list/")
    return render(request, 'login.html', {"title": "登录", "form": form})


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    # 清除session
    del request.session["info"]
    return redirect("/login/")


def image_code(request):
    """生成验证码"""
    code_img, code_str = check_code()
    print("code_str: ", code_str)

    # 将验证码存入session, 并设置过期时间, 单位秒
    request.session["code_str"] = code_str
    # 给session设置过期时间
    request.session.set_expiry(60*5) # 5分钟

    stream = BytesIO() # 内存中读取图片
    code_img.save(stream, "PNG")
    return HttpResponse(stream.getvalue())