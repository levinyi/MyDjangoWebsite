from pyexpat import model
from tabnanny import verbose
from unicodedata import name
from django.db import models
from matplotlib.pyplot import cla
from pkg_resources import require

# Create your models here.
class Admin(models.Model):
    """管理员表"""
    admin_name = models.CharField(max_length=60, verbose_name="管理员名")
    admin_pwd = models.CharField(max_length=60, verbose_name="管理员密码")

    def __str__(self):
        return self.admin_name

class Department(models.Model):
    """部门表"""
    title = models.CharField(verbose_name='部门标题', max_length=32)

    def __str__(self):
        return self.title


class UserInfo(models.Model):
    """员工表"""
    name = models.CharField(verbose_name="姓名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)
    age = models.IntegerField(verbose_name="年龄", default=18)
    account = models.DecimalField(
        verbose_name="账户余额", max_digits=10, decimal_places=2, default=0)

    # create_time = models.DateTimeField(verbose_name="注册时间", null=True, blank=True)
    create_time = models.DateField(verbose_name="入职时间", default="2021-11-11")

    # 级联删除
    depart = models.ForeignKey(verbose_name="部门", to="Department",
                               to_field="id", on_delete=models.CASCADE, null=True, blank=True)
    # 置空
    # depart = models.ForeignKey(to="Department", to_field="id", null=True, blank=True, on_delete=models.SET_NULL)

    # django中的约束
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(
        verbose_name="性别", choices=gender_choices, null=True, blank=True)
    
    
class PrettyNum(models.Model):
    '''靓号管理'''
    mobile = models.CharField(verbose_name="手机号", max_length=32)
    level_choice =(
        (1,"一级"),
        (2,"二级"),
        (3,"三级"),
        (4,"四级"),
    )
    level = models.SmallIntegerField(verbose_name="级别",choices=level_choice, default=1)
    status_choices = (
        (1,"已占用"),
        (2,"未占用"),
    )
    status = models.SmallIntegerField(verbose_name="状态",choices=status_choices, default=2)
    price = models.IntegerField(verbose_name="价格", default=0)


class Task(models.Model):
    """ 任务 """
    title = models.CharField(verbose_name="任务名称", max_length=64)
    content = models.TextField(verbose_name="任务内容")
    create_time = models.DateField(verbose_name="创建时间", auto_now_add=True)
    end_time = models.DateField(verbose_name="结束时间", null=True, blank=True)
    status_choices = (
        (1, "进行中"),
        (2, "已完成"),
        (3, "已取消"),
    )
    status = models.SmallIntegerField(verbose_name="任务状态", choices=status_choices, default=1)
    user = models.ForeignKey(verbose_name="任务所属人", to="Admin", to_field="id", on_delete=models.CASCADE) # 关联删除
    # user = models.ForeignKey(to="UserInfo", to_field="id", on_delete=models.CASCADE)
    # # 置空
    # user = models.ForeignKey(to="UserInfo", to_field="id", null=True, blank=True, on_delete=models.SET_NULL)
    level_choices = (
        (1, "一级"),
        (2, "二级"),
        (3, "三级"),
    )
    level = models.SmallIntegerField(verbose_name="任务级别", choices=level_choices, default=1)

