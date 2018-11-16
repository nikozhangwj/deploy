# -*- coding: utf-8 -*-
#
import uuid
import os
from django.conf import settings
from django.db import models
from ..pjenkins.exec_jenkins import JenkinsWork


class DeployList(models.Model):
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"
    FAILED = "FAILURE"
    LOG_DIR = os.path.join(settings.PROJECT_DIR, 'logs', 'deploy')
    DEPLOY_FILE_DIR = '/deploy/'

    STATUS_CHOICES = (
        (SUCCESS, SUCCESS),
        (RUNNING, RUNNING),
        (FAILED, FAILED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    app_name = models.CharField(max_length=1024)
    job_status = models.BooleanField(default=True)
    build_status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    log_path = models.CharField(max_length=256, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_build_time = models.DateTimeField(null=True)
    published_time = models.DateTimeField(null=True)
    build_console_output = models.TextField(blank=True)
    last_success_build_num = models.IntegerField(null=True)
    last_build_num = models.IntegerField(null=True)
    deploy_file_path = models.CharField(max_length=1024, null=True)

    def __str__(self):
        return self.app_name


def get_deploy_file_path(app_name):
    app = DeployList.objects.get(app_name=app_name)
    return app.deploy_file_path


def create_or_update(queryset):
    for job in queryset:
        if DeployList.objects.filter(app_name=job['name']):
            data = JenkinsWork().collect_job(name=job['name'])
            task = DeployList.objects.filter(app_name=job['name'])
            task.update(
                build_status=data.get('build_status', 'RUNNING'),
                last_build_time=data['last_build_time'],
                build_console_output=data['build_console_output'],
                last_success_build_num=data['last_success_build_num'],
                last_build_num=data['last_build_num'],
                deploy_file_path=os.path.join(DeployList.DEPLOY_FILE_DIR, job['name'], job['name']+'.jar')
            )
        else:
            data = JenkinsWork().collect_job(name=job['name'])
            DeployList.objects.create(
                app_name=data['app_name'],
                build_status=data.get('build_status', 'RUNNING'),
                last_build_time=data['last_build_time'],
                build_console_output=data['build_console_output'],
                last_success_build_num=data['last_success_build_num'],
                last_build_num=data['last_build_num'],
                deploy_file_path=os.path.join(DeployList.DEPLOY_FILE_DIR, job['name'], job['name'] + '.jar')
            )
