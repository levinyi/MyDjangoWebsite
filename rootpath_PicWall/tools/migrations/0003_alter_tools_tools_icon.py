# Generated by Django 4.0.4 on 2022-10-09 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0002_tools_tools_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tools',
            name='tools_icon',
            field=models.ImageField(blank=True, upload_to='images/tools_icon'),
        ),
    ]
