from django import forms

from django import forms
from django.core.files.base import ContentFile
from slugify import slugify
from urllib import request

from .models import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title','description')

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg','jpeg','png']
        extension = url.rsplit('.',1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError("The given URL does not match valid image extension.")
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super(ImageForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        image_name = '{0}{1}'.format(slugify(image.title), image_url.rsplit('.',1)[1].lower())
        response = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(response.read()), save=False)

        if commit:
            image.save()
        return image

'''
# 定义一个PhotoModelForm类
class PhotoModelForm(forms.ModelForm):
    class Meta:
        model = models.Image
        fields = ['title','description']
        # fields = ['photo_name', 'photo_time', 'photo_path','upload_time','owner','note']

    def clean_name(self):
        name = self.cleaned_data['title']
        if models.Image.objects.filter(name=name).exists():
            raise ValidationError('图片名已存在')
        return name

'''