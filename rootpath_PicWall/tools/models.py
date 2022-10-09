from tabnanny import verbose
from django.db import models

# Create your models here.
class Tools(models.Model):
    """小工具管理"""
    tools_name = models.CharField(verbose_name="小工具", max_length=64)
    tools_desc = models.TextField(verbose_name="功能表述")
    tools_freq = models.SmallIntegerField(verbose_name="使用频率",)
    tools_icon = models.ImageField(upload_to="images/tools_icon", blank=True)
