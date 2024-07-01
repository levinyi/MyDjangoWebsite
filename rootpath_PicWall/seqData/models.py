from django.db import models


# Create your models here.
class EndPoint(models.Model):
    name = models.CharField(max_length = 100, verbose_name="区域")
    endpoint = models.CharField(max_length = 100, verbose_name= "endpoint")

    def __str__(self):
        return self.name

def get_endpoint_choices():
    rcs = EndPoint.objects.all()
    choices = [(x.name, x.endpoint) for x in rcs]
    return choices

class CompanyInfo(models.Model):
    '''公司信息''' 
    name = models.CharField(verbose_name="公司名称", max_length=64)
    endpoint = models.CharField(max_length=255, choices=get_endpoint_choices())
    bucket = models.CharField(verbose_name="授权路径", max_length=300)
    KeyID = models.CharField(verbose_name="keyID", max_length=100)
    KeySecret = models.CharField(verbose_name="keySecret", max_length=100)

    def __str__(self):
        return self.name

class Data(models.Model):
    '''数据管理'''
    data_path = models.CharField(verbose_name="数据路径", max_length=332)
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, verbose_name="测序公司")
    area = models.ForeignKey(EndPoint, on_delete=models.CASCADE, verbose_name="区域")
    ctime = models.DateField(verbose_name="create time", auto_now_add=True, db_index=True)