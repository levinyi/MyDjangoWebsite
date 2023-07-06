import os
from celery import Celery
from django.conf import settings

# 设置默认的Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rootpath_PicWall.settings')

# 创建Celery应用
app = Celery('rootpath_PicWall')

# 加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()
