from http.client import HTTPResponse
from django.shortcuts import render
from .models import Tools

# Create your views here.
def tools_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    tools = Tools.objects.all()
    return render(request, 'tools/list_tools.html',{'tools':tools})

def tools_use(request, tools_name):
    if request.method == "GET":
        return render(request, 'tools_{}_use.html'.format(tools_name), {'tools_name':tools_name})
    elif request.method == "POST":
        user_ip = request.META['REMOTE_ADDR']
        print("user_ip: ", user_ip)
        tools_name()

