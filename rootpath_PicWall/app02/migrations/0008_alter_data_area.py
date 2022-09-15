# Generated by Django 4.0.4 on 2022-06-17 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app02', '0007_data_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='area',
            field=models.SmallIntegerField(choices=[(1, '华北'), (2, '华东'), (3, '华南')], default=1, verbose_name='区域'),
        ),
    ]
