# Generated by Django 4.0.4 on 2022-10-13 06:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('seqData', '0009_alter_companyinfo_endpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='ctime',
            field=models.DateField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='create time'),
            preserve_default=False,
        ),
    ]
