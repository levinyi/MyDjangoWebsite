import os
import re
from django.shortcuts import render
from app02 import models
from django.shortcuts import render, HttpResponse, redirect
from app01.utils.bootstrap import BootStrapModelForm

def tools_list(request):
    """数据列表"""
    # 去数据库中获取所有数据
    queryset = models.Tools.objects.all()
    return render(request, 'rootpath_tools_list.html',{'queryset':queryset})


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

def tools_use(request, tools_name):
    if request.method =="GET":
        return render(request, 'tools_{}_use.html'.format(tools_name),{'tools_name': tools_name})
    elif request.method == "POST":
        # 获取用户ip地址
        user_ip = request.META['REMOTE_ADDR']
        print("user_ip: ", user_ip)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if tools_name == "split_fasta":
            file_object = request.FILES.get("file_name") # 获取上传的文件
            result_path = BASE_DIR + "/tools/split_fasta/split_fasta_results"
            python_script = "python3 {}/tools/{}/{}.py".format(BASE_DIR, tools_name, tools_name)
            return save_file(request, result_path, python_script, file_object)
        elif tools_name == "pyxls":
            file_object = request.FILES.get("labRecord_file")
            well_file = request.FILES.get("well_file")
            total_volume = request.POST.get("total_volume")
            result_path = BASE_DIR + "/tools/pyxls/pyxls_results"
            python_script = "python3 {}/tools/{}/{}.py {}".format(BASE_DIR, tools_name, tools_name, total_volume)
            return save_file(request, result_path, python_script, file_object, well_file)
        elif tools_name == "plasmid_map":
            file_object = request.FILES.get("file_name")
            result_path = BASE_DIR + "/tools/plasmid_map/plasmid_map_results"
            end5_file = BASE_DIR + "/tools/plasmid_map/AAV6_Kan_5End_Region.fa"
            end3_file = BASE_DIR + "/tools/plasmid_map/AAV6_Kan_3End_Region.fa"
            python_script = "python3 {}/tools/{}/{}.py {} {} ".format(BASE_DIR, tools_name, tools_name, end5_file, end3_file)
            return save_file(request, result_path, python_script, file_object)
        elif tools_name == "MTP":
            file1 = request.FILES.get("file_name1")
            file2 = request.FILES.get("file_name2")
            volume = request.POST.get("volume")
            result_path = BASE_DIR + "/tools/project_MTP/MTP_results"
            python_script = "python3 {}/tools/project_MTP/{}.py {} ".format(BASE_DIR, tools_name, volume)
            return save_file(request, result_path, python_script, file1, file2)
        elif tools_name == "re-pooling":
            file1 = request.FILES.get("file_name1")
            file2 = request.FILES.get("file_name2")
            result_path = BASE_DIR + "/tools/project_re-pooling/re-pooling_results"
            python_script = "python3 {}/tools/project_re-pooling/{}.py ".format(BASE_DIR, tools_name)
            return save_file(request, result_path, python_script, file1, file2)
        elif tools_name == "normalization":
            file1 = request.FILES.get("file_name1")
            result_path = BASE_DIR + "/tools/project_normalization/normalization_results"
            python_script = "python3 {}/tools/project_normalization/{}.py ".format(BASE_DIR, tools_name)
            return save_file(request, result_path, python_script, file1)
        elif tools_name == "ReviewLocation":
            file1 = request.FILES.get("file_name1")
            result_path = BASE_DIR + "/tools/project_{}/{}_results".format(tools_name,tools_name)
            python_script = "python3 {}/tools/project_{}/{}.py ".format(BASE_DIR, tools_name, tools_name)
            return save_file(request, result_path, python_script, file1)
        


class ToolsModelForm(BootStrapModelForm):
    class Meta:
        model = models.Tools
        fields = '__all__'


def tools_update(request, tools_name):
    row_object = models.Tools.objects.get(tools_name=tools_name)

    if request.method == "GET":
        form = ToolsModelForm(instance=row_object)
        return render(request, 'tools_update.html'.format(tools_name), {'form':form, 'tools_name':tools_name})

    form = ToolsModelForm(request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/tools/list/')
    return render(request, 'tools_update.html'.format(tools_name), {'form':form,'tools_name':tools_name})