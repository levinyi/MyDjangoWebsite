import os
import uuid
import zipfile
from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.base import ContentFile

from .models import Tools, Result
from .tasks import execute_script_and_package


def tools_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    tools = Tools.objects.all()
    return render(request, 'tools/list_tools.html', {'tools': tools})

def get_result_path(BASE_DIR, tools_name):
    return os.path.join(BASE_DIR, f"rootpath_tools/project_{tools_name}/{tools_name}_results")

def tools_use(request, tools_name):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_ip = request.META['REMOTE_ADDR']
    if request.method == "GET":
        print("user_ip: {} is trying to use {} tools!".format(user_ip, tools_name))
        return render(request, 'tools/tools_{}_use.html'.format(tools_name), {'tools_name': tools_name})
    elif request.method == "POST":
        result_path = get_result_path(BASE_DIR, tools_name)
        # 从地下定义的函数中返回script_files和input_files.
        script_files, input_files = globals()[tools_name](request)
        python_script = f"python3 {BASE_DIR}/rootpath_tools/project_{tools_name}/{tools_name}.py {script_files}"
        print("result_path: ", result_path) # /home/dushiyi/my_web/rootpath_PicWall/rootpath_tools/project_Sanger_data_upload/Sanger_data_upload_results
        print("python_script: ", python_script) # python3 /home/dushiyi/my_web/rootpath_PicWall/rootpath_tools/project_Sanger_data_upload/Sanger_data_upload.py 20230612_AbCode01_1stBatch_Plasmid_Plate10
        print("input_files: ", input_files) # input_files:  [<TemporaryUploadedFile: Plate08.rar (application/octet-stream)>, <TemporaryUploadedFile: AbCode01_REF_Seq_for_SangerAnalysis_YHY20230520.txt (text/plain)>]
        if tools_name == "Sanger_data_upload":
            unique_id = str(uuid.uuid4())
            print("unique_id: ", unique_id) 
            # return save_file_status(request, result_path, python_script, input_files, unique_id, user_ip)
            return save_file_status(request, user_ip, tools_name, unique_id, result_path)
        return save_file(request, result_path, python_script, input_files)

def upload_file(file_name, project_path):
    file_name_name = file_name.name.replace(" ", "").replace('[',"").replace(']',"")  # 去掉文件名中的空格,[],
    file_path = os.path.join(project_path, file_name_name)  # result_path to project_path. Changed by dsy 20230612.
    os.makedirs(project_path, exist_ok=True)
    with open(file_path, 'wb+') as f:
        for chunk in file_name.chunks():
            f.write(chunk)
    return file_path

def save_file_status(request, user_ip, tools_name, unique_id, result_path):
    # os.system(f'rm -rf {result_path}/*')
    project_name = request.POST.get("project_name")
    project_path = os.path.join("/cygene4/pipeline/Sanger/data", project_name)
    # -- project_path: /cygene4/pipeline/Sanger/data/20230612_AbCode01_1stBatch_Plasmid_Plate10

    zip_file = request.FILES["file_name1"]  # zip file
    reference_file = request.FILES["file_name2"]  # fasta file

    # 将用户上传的文件保存到 result_path目录下
    zip_file_path = upload_file(zip_file, project_path)
    ref_file_path = upload_file(reference_file, project_path)

    result = Result.objects.create(
        unique_id = unique_id,
        tools_name = tools_name,
        result_path = project_path,
        user_ip= user_ip,
        status='pending',
        project_name = project_name
    )
    
    # 将文件分析任务加入异步任务队列
    execute_script_and_package.delay(user_ip, unique_id, zip_file_path, ref_file_path)

    # 返回唯一标识符给用户
    response_data = {
        'unique_id': unique_id,
        'check_available': "True",
    }
    return render(request, 'tools/tools_Sanger_data_upload_use.html', response_data)


def check_status(request):
    if request.method == "GET":
        queryset = Result.objects.all().order_by("-id")
        return render(request, 'tools/check_status.html', {"queryset":queryset})

    unique_id = request.POST.get('unique_id')
    try:
        result = Result.objects.get(unique_id=unique_id)
        if result is None:
            context = {
                'error_message': f'Result with unique ID {unique_id} not found.'
            }
            return render(request, 'tools/check_status.html', context)
        context = {
            'result': result,
            'download_available': result.status == "completed"
        }
        return render(request, 'tools/check_status.html', context)
    except Result.DoesNotExist:
        context = {
            'error_message': f'Result with unique ID {unique_id} not found.'
        }
        return render(request, 'tools/check_status.html', context)

def download_result(request, unique_id):
    try:
        result = Result.objects.get(unique_id=str(unique_id))

        if result.status != "completed":
            return HttpResponse("任务尚未完成，无法下载")

        result_path = result.result_path
        print("result_path: ",result_path)
        if not os.path.exists(result_path):
            return HttpResponse("result path have been deleted by someone.")
        
        zip_file_name = os.path.basename(result_path) + ".zip"
        full_zip_file = os.path.join(result_path, zip_file_name)
        print("full_zip_file: ", full_zip_file)
        
        if not os.path.exists(full_zip_file):
            print("file does not exists!")
            return HttpResponse("file does not exists")
        
        print("starting open zip file to response!")
        with open(full_zip_file, "rb") as f:
            response = HttpResponse(f)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{zip_file_name}"'
            return response
    except Result.DoesNotExist:
        return HttpResponse(f"Result with unique ID {unique_id} not found.")

def save_file(request, result_path, python_script, input_file_list):
    '''定义一个函数, 用来保存用户上传的文件(可以有多个文件),且将文件传递给python脚本,并将脚本执行后的结果打包成zip文件, 并发送给浏览器'''
    # 先删除result_path下的所有文件(是上一个用户运行的结果) bugs here: 用户没有上传文件，但点击了开始按钮，这时网页会报错，同时后台也会删除结果.
    os.system(f'rm -rf {result_path}/*')
    print(f"Remove: rm -rf {result_path}/*")

    '''保存用户上传的文件到本地'''
    file_list = []  # 文件顺序是根据每个功能函数中append的顺序
    for file_object in input_file_list:
        # 将用户上传的文件保存到 result_path目录下
        file_name = file_object.name.replace(" ", "").replace('[',"").replace(']',"")  # 去掉文件名中的空格,[],
        # print("file_name: ", file_name) # 文件名, 没有路径, 只有文件名, 如: "test.txt"
        file_path = os.path.join(result_path, file_name)
        # file_path: 文件全路径, 如: "/rootpath_PicWall/tools/split_fasta_results/test.txt"
        # print("file_path: ", file_path)
        file_list.append(file_path)
        # print("这是文件存储在服务器上的全路径: {}/tools/{}/{}".format(BASE_DIR,result_path,file_path))
        with open(file_path, 'wb+') as f:
            for chunk in file_object.chunks():
                f.write(chunk)
    print(f"Save files to result_path: {result_path}")
    
    '''执行脚本进行文件处理'''
    print('{} {} {}'.format(python_script, " ".join(file_list), result_path))
    os.system('{} {} {}'.format(python_script, " ".join(file_list), result_path))  # 调用python脚本
    # 等待系统执行分析脚本，完成后才能继续向下走：
    # 将result_path下的所有文件打包成zip文件
    result_name = result_path.split("/")[-1]
    # print("result_name : ", result_name)
    os.system(f'zip -q -j {result_path}/{result_name}.zip {result_path}/*')  # 调用zip脚本打包
    print("打包结果文件中...")
    # 将zip文件发送给浏览器
    with open(os.path.join(result_path, result_name + '.zip'), 'rb') as f:
        response = HttpResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="{result_name}.zip"'
        print("文件打包完成，已返回前端页面")
        return response

def delete_result(request, result_path):
    '''定义一个函数, 用来删除用户的结果和上传的文件'''
    # 删除result_path目录
    os.system(f'rm -rf {result_path}')
    print(f"Remove: rm -rf {result_path}")
    # 再删除数据库中的记录
    Result.objects.filter(result_path=result_path).delete()
    return HttpResponse("删除成功！")

#### 以下是执行各个工具的文件处理函数。

def split_fasta(request):
    """1 input file"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name"))
    return script_files, input_files


def normalization(request):
    """1 input file and 0 argument"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    return script_files, input_files


def ReviewLocation(request):
    """
    attention the order of input_files.
    1 input file and 0 argument
    """
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    return script_files, input_files

def re_pooling(request):
    """2 input files"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    input_files.append(request.FILES.get("file_name2"))
    return script_files, input_files

def excel_table_merge(request):
    """2 input files"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    input_files.append(request.FILES.get("file_name2"))
    return script_files, input_files

def MTP(request):
    """2 input files and 1 argument"""
    script_files = request.POST.get("volume")
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    input_files.append(request.FILES.get("file_name2"))
    return script_files, input_files


def pyxls(request):
    """2 input files"""
    script_files = request.POST.get("total_volume")
    input_files = []
    input_files.append(request.FILES.get("labRecord_file"))
    input_files.append(request.FILES.get("well_file"))
    return script_files, input_files


def plasmid_map(request):
    """2 input files"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name"))
    input_files.append(request.FILES.get("file_name2"))
    return script_files, input_files


def Sanger_data_upload(request):
    """2 input files and 1 argument ;upload sanger data"""
    script_files = request.POST.get("project_name")
    input_files = []
    input_files.append(request.FILES.get("file_name1"))  # zip file
    input_files.append(request.FILES.get("file_name2"))  # fasta file
    return script_files, input_files