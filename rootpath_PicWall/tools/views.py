import os
import subprocess
import  pandas as pd
import uuid
import django.utils.timezone as timezone    # 使用timezone.now()获取当前时间
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from project_management.models import GeneSynEnzymeCutSite
from project_management.project_scripts.generate_REQIN import check_forbiden_seq

from .models import Inquiry, InquiryGeneSeqValidation, Tools, Result
from .tasks import execute_script_and_package
from seqData.utils.pagination import Pagination


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
        return render(request, 'tools/tools_{}_use.html'.format(tools_name), {'tools_name': tools_name})
    elif request.method == "POST":
        result_path = get_result_path(BASE_DIR, tools_name)
        # 从下面定义的函数中返回script_files和input_files.
        script_files, input_files = globals()[tools_name](request)
        print("input_files: ", input_files)
        python_script = f"python3 {BASE_DIR}/rootpath_tools/project_{tools_name}/{tools_name}.py {script_files}"
        print("python_script: ", python_script)
        if tools_name == "Sanger_data_upload":
            unique_id = str(uuid.uuid4())
            return save_file_status(request, user_ip, tools_name, unique_id)
        elif tools_name == "split_384_to_96":
            return split_384_to_96_main(result_path, input_files)
        return save_file(request, result_path, python_script, input_files)

def upload_file(file_name, project_path):
    # 去掉文件名中的空格,[],()
    file_name_name = file_name.name.replace(" ", "").replace('[',"").replace(']',"")  
    file_name_name = file_name_name.replace("(","").replace(")","")
    file_path = os.path.join(project_path, file_name_name)  # result_path to project_path. Changed by dsy 20230612.
    os.makedirs(project_path, exist_ok=True)
    with open(file_path, 'wb+') as f:
        for chunk in file_name.chunks():
            f.write(chunk)
    return file_path

def save_file_status(request, user_ip, tools_name, unique_id):
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
    # if request.method == "GET":
    queryset = Result.objects.all().order_by("-id")

    page_obj = Pagination(request, queryset, page_size=20, page_param="page", plus=5)
    context = {
        "queryset": page_obj.page_queryset,
        "page_string": page_obj.html()
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
        # file_name = file_object.name.replace(" ", "").replace('[',"").replace(']',"")  # 去掉文件名中的空格,[],
        file_name = file_object.name.replace(" ", "")  # 去掉文件名中的空格
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

def delete_result(request, unique_id):
    result = Result.objects.get(unique_id=unique_id)
    result_path = result.result_path
    
    user_ip  = request.META['REMOTE_ADDR']
    if result.user_ip != user_ip:
        return HttpResponse("You can not delete this result.")
    else:
        subprocess.run(f'rm -rf {result_path}', shell=True, check=True)
        result.delete()
    return redirect('tools:check_status')

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

def split_384_to_96(request):
    """1 input json data and 0 argument"""
    script_files = ""
    input_data = request.POST.get("tableData")
    print("type of input_data: ", type(input_data))
    return script_files, input_data

def split_384_to_96_main(result_path, input_files):
    input_data = eval(input_files)
    df = pd.DataFrame(input_data)
    df.set_index(0, inplace=True)

    df.columns = df.iloc[0]
    df = df[1:]
    # df = df.astype(int)

    data = df.to_numpy()
    # 十字分法
    # 将16x24的数据拆分成4个8x12的数据 
    # plates = [data[i*8:(i+1)*8, j*12:(j+1)*12] for i in range(2) for j in range(2)]
    # 田字分法
    sub_array = []
    sub_array.append(data[::2, ::2])
    sub_array.append(data[1::2, ::2])
    sub_array.append(data[::2, 1::2])
    sub_array.append(data[1::2, 1::2])
    plates = sub_array
    # print(plates)

    # 将4个8x12的数据转换成dataframe并写入到同一个excel文件中，写入同一个sheet中, 每个plate直接空行隔开,
    # 写入的时候，还要把 A-H的行索引和1-12的列索引写入到excel文件中。
    with pd.ExcelWriter(os.path.join(result_path, 'result.xlsx'), engine='xlsxwriter', mode='w') as writer:
        row = 1
        for i, plate in enumerate(plates):
            df = pd.DataFrame(plate)
            if i != 0:
                # 每个plate之间空一行
                row += 1
            df.to_excel(writer, sheet_name='Sheet1', startrow=row, startcol=1, index=False, header=False)
        
            worksheet = writer.sheets['Sheet1']
            # 设置行列索引
            for x, col_label in enumerate('ABCDEFGH'):
                worksheet.write(x + row, 0, col_label)
            for j, row_label in enumerate(range(1, 13)):
                worksheet.write(row-1, j+1, row_label)
            
            # 更新下一个plate的起始行
            row += 9
    
    # 将result_path下的result.xlsx文件返回给用户
    with open(os.path.join(result_path, 'result.xlsx'), 'rb') as f:
        response = HttpResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment;filename="result.xlsx"'
        return response

def genesyn_cal_len(request):
    """2 input files"""
    script_files = ""
    input_files = []
    input_files.append(request.FILES.get("file_name1"))
    input_files.append(request.FILES.get("file_name2"))
    return script_files, input_files

import json
import requests
def get_access_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal/"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get("tenant_access_token")

def write_data_to_feishu_Sheet(request):
    """write data to feishu Sheet"""
    if request.method == "GET":
        return render(request, 'tools/write_data_to_feishu_Sheet.html')
    elif request.method == "POST":
        sheet_url = request.POST.get("sheet_url")
        field1 = request.POST.get("field1")
        field2 = request.POST.get("field2")
        field3 = request.POST.get("field3")

        app_token = sheet_url.split("/")[-1].split("?")[0]
        table_id = sheet_url.split("/")[-1].split("?")[1].split("=")[1].split("&")[0]
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        payload = json.dumps({
            "fields": {
                "Multiline": f"{field1}",
                "Name": f"{field2}",
                "Person": f"{field3}"
            }
        })
        app_id = "cli_a412acc70c23500c"
        app_secret = "3jGYpDlV7hCLRjFhXeSfibWo7lTottuh"

        # 获取访问令牌
        access_token = get_access_token(app_id, app_secret)

        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return HttpResponse(response.text.encode('utf8'))

def temp_check_forbiden_seq(seq, seq_length, customer_forbidden_list=None):
    '''根据序列长度检查正义和反义链'''
    seq = seq.upper().replace(" ", "")

    forbidden_list_objects = GeneSynEnzymeCutSite.objects.all()
    raw_forbidden_list = []
    forbidden_list = []
    for enzyme in forbidden_list_objects:
        enzyme_name = enzyme.enzyme_name
        enzyme_seq = enzyme.enzyme_seq
        enzyme_scope = enzyme.usescope
        start,end = enzyme_scope.split("-")
        start = int(start)
        end = int(end)

        if start <= seq_length <= end:
            forbidden_list.append(enzyme_seq)
        raw_forbidden_list.append(enzyme_seq)
    print("company forbidden_list: ", forbidden_list)
    if customer_forbidden_list and isinstance(customer_forbidden_list, str):
        formated_list = customer_forbidden_list.split(",")
        forbidden_list.extend(formated_list)
    print("forbidden_list + customer list: ", forbidden_list)
    # 检查序列中是否包含禁止的序列
    raw_forbidden_list.extend(customer_forbidden_list.split(","))
    contained_forbidden_list = [forbiden_seq for forbiden_seq in forbidden_list if forbiden_seq in seq]    

    return contained_forbidden_list, raw_forbidden_list

@login_required
@require_POST
def inquiry_create(request):
    try:
        data = json.loads(request.body)
        gene_number = 0
        for row in data:
            if any(cell is not None for cell in row): 
                gene_number += 1

        inquiry_object = Inquiry.objects.create(
            user=request.user,
            gene_number=gene_number,
            validated_number=0,
            create_date=timezone.now(),
            status="created"
        )

        for row in data:
            if any(cell is not None for cell in row): 
                combined_seq = str(row[1] + row[2] + row[3]).upper()
                contained_forbidden_list, raw_forbidden_list = temp_check_forbiden_seq(combined_seq, len(combined_seq), row[4])
                
                if contained_forbidden_list: 
                    for forbidden_seq in contained_forbidden_list:
                        combined_seq = combined_seq.replace(forbidden_seq, f'<em class="bg-warning">{forbidden_seq}</em>')
                        seq_status = "forbidden"
                else:
                    seq_status = "validated"
                    combined_seq = combined_seq

                gene_data = InquiryGeneSeqValidation.objects.create(
                    user = request.user,
                    inquiry_id = inquiry_object,
                    gene_name = row[0],
                    seq5NC = row[1],
                    seqAA = row[2],
                    seq3NC = row[3],
                    forbid_seq = raw_forbidden_list,
                    combined_seq = combined_seq,
                    saved_seq = combined_seq,
                    status = seq_status,
                )
        return JsonResponse({'status': 'success', 'id': inquiry_object.id, "message": "Data saved successfully"})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def inquiry_list(request):
    if request.method == "GET":
        user = request.user
        inquiry_list = Inquiry.objects.filter(user=user)
        return render(request, 'tools/inquiry_list.html',{'inquiry_list': inquiry_list})

@login_required
def inquiry_detail(request, pk):
    ''' when user click the "Analysis" button, this function will be called.'''
    if request.method == "GET":
        user = request.user

        gene_list = InquiryGeneSeqValidation.objects.filter(user=user, inquiry_id=pk)
        new_gene_list = []
        for gene in gene_list:
            new_gene_list.append({
                "gene_name": gene.gene_name,
                "original_seq": gene.combined_seq,
                "saved_seq": gene.saved_seq,
                "status": gene.status,
                "forbid_seq": gene.forbid_seq,
                "inquiry_id": gene.inquiry_id.id,
            })

        return render(request, 'tools/inquiry_detail.html',{'new_gene_list': new_gene_list})

@login_required
def inquiry_delete(request, pk):
    try:
        inquiry = get_object_or_404(Inquiry, id=pk, user=request.user)
        inquiry.delete()
        return redirect('/tools/inquiry_list/')
    except Inquiry.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Inquiry not found'})

@require_POST
def inquiry_validation(request, pk):
    ''' when user click the "validate" button, this function will be called. '''
    try:
        user = request.user
        data = json.loads(request.body.decode('utf-8'))

        saved_seq = data.get("sequence")
        gene_id = data.get("gene")

        gene_object = InquiryGeneSeqValidation.objects.get(user=user, inquiry_id=pk, gene_name=gene_id)

        original_seq = gene_object.combined_seq
        if original_seq == saved_seq:
            return JsonResponse({'status': 'error', 'message': 'No changes made.'})
        
        forbidden_list = temp_check_forbiden_seq(saved_seq, len(saved_seq), gene_object.forbid_seq)

        if forbidden_list: 
            for forbidden_seq in forbidden_list:
                saved_seq = saved_seq.replace(forbidden_seq, f'<em class="bg-warning">{forbidden_seq}</em>')
            gene_status = 'forbidden'
        else:
            gene_status = 'validated'
        
        print("gene_status: ", gene_status)
        gene_object.status = gene_status
        gene_object.saved_seq = saved_seq
        gene_object.save()

        return JsonResponse({'status': 'success', 'message': 'validation process finished'})
    except InquiryGeneSeqValidation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'InquiryGeneSeqValidation not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def inquiry_save(request, pk):
    try:
        user = request.user
        data = json.loads(request.body.decode('utf-8'))

        gene_id = data.get("gene")

        gene_object = InquiryGeneSeqValidation.objects.get(user=user, inquiry_id=pk, gene_name=gene_id)
        
        gene_object.status = 'saved'
        gene_object.save()

        return JsonResponse({'status': 'success', 'message': 'validation process finished'})
    except InquiryGeneSeqValidation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'InquiryGeneSeqValidation not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def inquiry_download(request, pk):
    try:
        user = request.user
        inquiry_object = Inquiry.objects.get(user=user, id=pk)
        gene_list = InquiryGeneSeqValidation.objects.filter(user=user, inquiry_id=pk)

        new_gene_list = []
        for gene in gene_list:
            new_gene_list.append({
                "gene_name": gene.gene_name,
                "original_seq": gene.combined_seq,
                "saved_seq": gene.saved_seq,
                "status": gene.status,
                "forbid_seq": gene.forbid_seq,
                "inquiry_id": gene.inquiry_id.id,
                "Seq5NC": gene.seq5NC,
                "Seq3NC": gene.seq3NC,
            })
        
        df = pd.DataFrame(new_gene_list)
        columns = ['GeneName','Seq5NC','SeqAA','Seq3NC','ForbiddenSeqs','VectorID','Species']

        df.set_index("gene_name", inplace=True)
        df.to_excel(f"/cygene4/pipeline/GeneSyn/tmp/{user}_inquiry_{pk}.xlsx")
        with open(f"/cygene4/pipeline/GeneSyn/tmp/{user}_inquiry_{pk}.xlsx", 'rb') as f:
            response = HttpResponse(f)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="inquiry_{inquiry_object.id}.xlsx"'
            return response
        
    except Inquiry.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Inquiry not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})