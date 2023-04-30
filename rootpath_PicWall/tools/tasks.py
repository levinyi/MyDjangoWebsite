from __future__ import absolute_import, unicode_literals
from my_celery import app
import os
import zipfile
from .models import Result
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task()
def execute_script_and_package(result_path, python_script, file_list, unique_id,user_ip):
    print("Executing execute_script_and_package task")
    # execute_script_and_package(result_path, python_script, file_list, unique_id)
    update_task_status(result_path, 'in_progress', unique_id, user_ip)

    # 执行Python脚本
    logger.info('{} {} {}'.format(python_script, " ".join(file_list), result_path))  # 调用python脚本
    os.system('{} {} {}'.format(python_script, " ".join(file_list), result_path))  # 调用python脚本

    # 打包文件
    result_name = os.path.basename(result_path) +'.zip'
    os.system(f'zip -q -j {result_path}/{result_name} {result_path}/het.txt {result_path}/sum.txt')  # 调用zip脚本打包

    # 更新任务状态为已完成
    update_task_status(result_path, 'completed', unique_id, user_ip)

@app.task()
def update_task_status(result_path, status, unique_id,user_ip):
    # 更新数据库中的任务状态和数据文件路径
    result = Result.objects.get(unique_id=unique_id, user_ip=user_ip)
    result.status = status
    result.save()
