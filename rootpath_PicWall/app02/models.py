from django.db import models

# Create your models here.
class Data(models.Model):
    '''数据管理'''
    area_choices = (
        (1, "华北"),
        (2, "华东"),
        (3, "华南"),
    )
    data_path = models.CharField(verbose_name="数据路径", max_length=332)
    area = models.SmallIntegerField(verbose_name="区域", choices=area_choices)
    class Mete:
        app_label = 'app02'

class Photo(models.Model):
    """图片管理"""
    photo_name = models.CharField(verbose_name="图片名称", max_length=64)
    photo_time = models.DateField(verbose_name="拍摄时间",)
    photo_path = models.ImageField(upload_to="photos/", verbose_name="图片路径")
    upload_time = models.DateField(verbose_name="上传时间",)
    owner = models.CharField(verbose_name="拥有人", max_length=32)
    note = models.TextField(verbose_name="介绍",null=True, blank=True)

class Tools(models.Model):
    """小工具管理"""
    tools_name = models.CharField(verbose_name="小工具", max_length=64)
    tools_desc = models.TextField(verbose_name="功能表述")