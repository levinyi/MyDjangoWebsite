import subprocess
from my_celery import app
import os
from django.utils import timezone
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