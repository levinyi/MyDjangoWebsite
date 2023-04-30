# Generated by Django 4.0.4 on 2023-04-29 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0004_alter_tools_tools_icon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_id', models.CharField(max_length=255, unique=True)),
                ('result_path', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('user_ip', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
