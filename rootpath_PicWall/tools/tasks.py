import subprocess
from my_celery import app
import os
from django.utils import timezone

from project_management.project_scripts.feishu import send_message
from .models import Result
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task()
def update_task_status(status, unique_id, user_ip, end_time=None):
    # 更新数据库中的任务状态和数据文件路径
    result = Result.objects.get(unique_id=unique_id, user_ip=user_ip)
    result.status = status
    if end_time:
        result.end_time = end_time
    result.save()


@app.task()
def execute_script_and_package(user_ip, unique_id, zip_file_path, ref_file_path):
    # 更新任务状态为"执行中"
    update_task_status('in_progress', unique_id, user_ip)

    # 从数据库中读取本次项目的信息：
    result = Result.objects.get(unique_id=unique_id, user_ip=user_ip)
    project_name = result.project_name
    result_path = result.result_path

    # 执行Python脚本
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_dir = os.path.join(BASE_DIR, f'rootpath_tools/project_Sanger_data_upload')
    subprocess.run(f'python {script_dir}/Sanger_data_upload.py -n {project_name} -a {zip_file_path} -r {ref_file_path}', shell=True)  # 调用python脚本
    # 更新任务状态为"打包中"
    update_task_status('packaging', unique_id, user_ip)

    # 打包文件
    full_zip_path = os.path.join(result_path, os.path.basename(result_path) + '.zip')

    subprocess.run(f'xargs -a {result_path}/{project_name}.archive.selected.txt zip -q -j {full_zip_path}', shell=True, check=True)

    # 更新任务状态为"已完成"
    end_time = timezone.now()
    update_task_status('completed', unique_id, user_ip, end_time=end_time)
    
    # send message to user.
    # sendMesage()

@app.task()
def Multi_Frag_Sanger_main_task(user_ip, unique_id, zip_file_path, ref_file_path):
    # 更新任务状态为 "执行中"
    update_task_status('in_progress', unique_id, user_ip)

    # 从数据库中读取本次项目的信息：
    result = Result.objects.get(unique_id=unique_id, user_ip=user_ip)
    project_name = result.project_name
    result_path = result.result_path

    # 执行Python脚本
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_dir = os.path.join(BASE_DIR, f'rootpath_tools/project_Multi_Frag_Sanger')
    subprocess.run(f'python {script_dir}/Multi_Frag_Sanger.py -n {project_name} -a {zip_file_path} -r {ref_file_path}', shell=True)  # 调用python脚本
    # 更新任务状态为"打包中"
    update_task_status('packaging', unique_id, user_ip)

    # 打包文件
    full_zip_path = os.path.join(result_path, os.path.basename(result_path) + '.zip')

    subprocess.run(f'xargs -a {result_path}/need_to_be_packaged.txt zip -q -j {full_zip_path}', shell=True, check=True)

    # 更新任务状态为"已完成"
    end_time = timezone.now()
    update_task_status('completed', unique_id, user_ip, end_time=end_time)
    
    # send message to user.
    # sendMesage()


@app.task()
def codonOptimization_task(user_ip, unique_id, optimization_method, file_path, access_token, email):
    update_task_status('running', unique_id, user_ip)

    result = Result.objects.get(unique_id=unique_id, user_ip=user_ip)
    project_name = result.project_name
    result_path = result.result_path

    print(optimization_method)
    # 执行Python脚本: SACfIv1 to GeneSyn
    if optimization_method == 'LongGene_Relax':
        subprocess.run(f"python /cygene4/pipeline/OEPCR/User_Seq_To_SACFlv1.py {file_path} {result_path} 2 ", shell=True)
        subprocess.run(f"python /cygene4/pipeline/OEPCR/batch_run.py {result_path} 2", shell=True)
    elif optimization_method == 'NoFoldingCheck':
        subprocess.run(f"python /cygene4/pipeline/OEPCR/User_Seq_To_SACFlv1.py {file_path} {result_path} 1 ", shell=True)
        subprocess.run(f"python /cygene4/pipeline/OEPCR/batch_run.py {result_path} 1", shell=True)
    elif optimization_method == 'FbdSeqOnly':
        subprocess.run(f"python /cygene4/pipeline/OEPCR/User_Seq_To_SACFlv1.py {file_path} {result_path} 0 ", shell=True)
        subprocess.run(f"python /cygene4/pipeline/OEPCR/batch_run.py {result_path} 0", shell=True)
    else:
        print("Error: optimization_method is not valid.")
    # 把result_path下所有txt文件都写入到need_to_be_packaged.txt中
    txt_files = [os.path.join(result_path, file) for file in os.listdir(result_path) if file.endswith('.txt')]
    # print("txt_files: ", txt_files)
    with open(os.path.join(result_path, 'need_to_be_packaged.txt'), 'w') as f:
        for file in txt_files:
            f.write(file + '\n')
    
    # Step2: find the output file
    full_zip_path = os.path.join(result_path, os.path.basename(result_path) + '.zip')
    subprocess.run(f"xargs -a {result_path}/need_to_be_packaged.txt zip -q -j {full_zip_path}", shell=True, check=True)

    # 最终更新状态
    end_time = timezone.now()
    update_task_status('completed', unique_id, user_ip, end_time=end_time)

    # 发送邮件通知
    message = f"项目 '{project_name}' 分析完成"
    send_message(access_token, message, 'email', email)
    
    return
