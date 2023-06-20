from django.db import models


# Create your models here.
class Tools(models.Model):
    """小工具管理"""
    tools_name = models.CharField(verbose_name="小工具", max_length=64)
    tools_desc = models.TextField(verbose_name="功能表述")
    tools_freq = models.SmallIntegerField(verbose_name="使用频率",)
    tools_icon = models.ImageField(upload_to="static/img/tools_icon", blank=True)

def generate_upload_path(instance, filename):
    # 使用实例对象的 tools_name 和 unique_id 生成动态路径
    upload_path = f'rootpath_tools/project_{instance.tools_name}/project_{instance.tools_name}_results/{filename}'
    return upload_path

class Result(models.Model):
    """store result path"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress','in_progress'),
        ('completed','Completed'),
    ]
    unique_id = models.CharField(max_length=255, unique=True)
    user_ip = models.CharField(max_length=255)  # 新增字段，用于保存用户的 IP 地址
    tools_name = models.CharField(max_length=255, null=True,blank=True)
    project_name = models.CharField(max_length=255,null=True, blank=True)
    result_path = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.unique_id
