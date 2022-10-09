from django.db import models
from django.contrib.auth.models import User

#pip3 install awesome-slugify
from slugify import slugify

# Create your models here.

class Image(models.Model):
    """图片管理"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")
    title = models.CharField(verbose_name="图片名称", max_length=300)
    url = models.URLField()
    slug = models.SlugField(max_length=500, blank=True)
    
    description = models.TextField(verbose_name="介绍",null=True, blank=True)
    created = models.DateField(verbose_name="上传时间",auto_now_add=True, db_index=True)
    image = models.ImageField(upload_to="photo/%Y/")

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Image, self).save(*args, **kwargs)