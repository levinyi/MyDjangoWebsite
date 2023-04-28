from django.shortcuts import redirect,render,HttpResponse 
from django.utils.deprecation import MiddlewareMixin

class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        
        # 0. 排除那些不需要验证的url
        if request.path not in ['/photo/list/']:
            return None
        
        # 1.读取当前访问用户的session信息，如果能读到，则认为用户已经登录，就可以访问后台管理界面
        info_dict = request.session.get("info")
        if info_dict:
            return None
        
        # 2.如果没有登录，则跳转到登录界面
        return redirect("/login/")

