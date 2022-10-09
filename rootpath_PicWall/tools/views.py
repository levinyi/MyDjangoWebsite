import os
from django.http import HttpResponse
from django.shortcuts import render

from rootpath_PicWall.settings import BASE_DIR
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
        # get submit times data and save to database model
        print("user_ip: ", user_ip)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result_path = BASE_DIR + "/rootpath_tools/project_{}/{}_results".format(tools_name,tools_name)

        script_files, input_files = globals()[tools_name](request, tools_name)
        python_script = "python3 {}/rootpath_tools/project_{}/{}.py {}".format(BASE_DIR, tools_name, tools_name, script_files)
        return save_file(request, result_path, python_script, input_files)


def save_file(request, result_path, python_script, *file_object_list):
    '''定义一个函数, 用来保存用户上传的文件(可以有多个文件),且将文件传递给python脚本,并将结果打包成zip文件, 并发送给浏览器'''
    # 先删除result_path下的所有文件(是上一个用户运行的结果)
    os.system('rm -rf {}/*'.format(result_path))
    print("Remove: rm -rf {}/*".format(result_path))
    
    file_list = [] # 文件顺序是怎么样的？按照用户上传的顺序？需要测试一下
    for file_object in file_object_list:
        # 将用户上传的文件保存到result_path目录下
        file_name = file_object.name.replace(" ","") # 去掉文件名中的空格
        # print("file_name: ", file_name) # 文件名,没有路径, 只有文件名, 如: "test.txt"
        file_path = os.path.join(result_path, file_name) # 文件全路径, 如: "/rootpath_PicWall/app02/tools/split_fasta/split_fasta_results/test.txt"
        # print("file_path: ", file_path)
        file_list.append(file_path)
        # print("这是文件存储在服务器上的全路径: {}/tools/{}/{}".format(BASE_DIR,result_path,file_path))
        with open(file_path, 'wb+') as f:
            for chunk in file_object.chunks():
                f.write(chunk)
    print("Save files to result_path: {}".format(result_path))
    os.system('{} {} {}'.format(python_script, " ".join(file_list), result_path)) # 调用python脚本
    print('{} {} {}'.format(python_script, " ".join(file_list), result_path))
    # 将result_path下的所有文件打包成zip文件
    result_name = result_path.split("/")[-1]
    # print("result_name : ", result_name)
    os.system('zip -q -j {}/{}.zip {}/*'.format(result_path, result_name, result_path)) # 调用zip脚本
    print("打包结果文件中...")
    # 将zip文件发送给浏览器
    with open(result_path+'/'+ result_name+'.zip', 'rb') as f:
        response = HttpResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}.zip"'.format(result_name)
        return response


def ReviewLocation(request):
    """attention the order of those files"""
    script_files = ""
    input_files = request.FILES.get("file_name1")
    return script_files, input_files

def normalization(request):
    script_files = ""
    input_files = request.FILES.get("file_name1")
    return script_files, input_files

def re_pooling(request):
    script_files = ""
    input_files = request.FILES.get("file_name1")
    input_files = input_files + " " + request.FILES.get("file_name2")
    return script_files, input_files

def MTP(request):
    script_files = request.POST.get("volume")
    input_files = request.FILES.get("file_name1")
    input_files = input_files + " " + request.FILES.get("file_name2")
    return script_files, input_files

def plasmid_map(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_files = BASE_DIR + "/rootpath_tools/project_plasmid_map/AAV6_Kan_5End_Region.fa"
    script_files = script_files + " " + BASE_DIR + "/rootpath_tools/project_plasmid_map/AAV6_Kan_3End_Region.fa"
    input_files = request.FILES.get("file_name")
    return script_files, input_files

def pyxls(request):
    script_files = request.POST.get("total_volume")
    input_files = request.FILES.get("labRecord_file")
    input_files = input_files + " " + request.FILES.get("well_file")
    return script_files, input_files

def split_fasta(request):
    script_files = ""
    input_files = request.FILES.get("file_name")
    return script_files, input_files
