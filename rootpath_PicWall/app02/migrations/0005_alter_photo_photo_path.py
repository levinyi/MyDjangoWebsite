# Generated by Django 4.0.4 on 2022-05-30 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app02', '0004_alter_photo_photo_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='photo_path',
            field=models.ImageField(upload_to='photos/', verbose_name='图片路径'),
        ),
    ]
