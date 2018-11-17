# Generated by Django 2.1 on 2018-11-13 06:11

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeployList',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('app_name', models.CharField(max_length=1024)),
                ('job_status', models.BooleanField(default=True)),
                ('build_status', models.CharField(choices=[('success', 'success'), ('running', 'running'), ('failed', 'failed')], max_length=128)),
                ('log_path', models.CharField(blank=True, max_length=256, null=True)),
                ('create_time', models.TimeField(auto_now_add=True)),
                ('last_build_time', models.TimeField(null=True)),
                ('build_console_output', models.TextField(blank=True)),
            ],
        ),
    ]
