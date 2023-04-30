from django.db import models


# Create your models here.
class Tools(models.Model):
    """小工具管理"""
    tools_name = models.CharField(verbose_name="小工具", max_length=64)
    tools_desc = models.TextField(verbose_name="功能表述")
    tools_freq = models.SmallIntegerField(verbose_name="使用频率",)
    tools_icon = models.ImageField(upload_to="static/img/tools_icon", blank=True)

class Result(models.Model):
    """store result path"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed','Completed'),
    ]
    unique_id = models.CharField(max_length=255, unique=True)
    result_path = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user_ip = models.CharField(max_length=255)  # 新增字段，用于保存用户的 IP 地址
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.unique_id
