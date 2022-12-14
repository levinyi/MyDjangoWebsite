# Generated by Django 4.0.4 on 2022-04-25 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_alter_userinfo_age'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='部门标题')),
            ],
        ),
        migrations.AddField(
            model_name='userinfo',
            name='account',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='账户余额'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='create_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='注册时间'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='gender',
            field=models.SmallIntegerField(blank=True, choices=[(1, '男'), (2, '女')], null=True, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='age',
            field=models.IntegerField(default=18, verbose_name='年龄'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='name',
            field=models.CharField(max_length=32, verbose_name='姓名'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='password',
            field=models.CharField(max_length=64, verbose_name='密码'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='depart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.department'),
        ),
    ]
