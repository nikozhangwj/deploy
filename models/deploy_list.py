# -*- coding: utf-8 -*-
#
import uuid
import os
import shutil
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ..pjenkins.exec_jenkins import JenkinsWork
from datetime import datetime


class DeployList(models.Model):
    SUCCESS = "SUCCESS"
    RUNNING = "RUNNING"
    FAILED = "FAILURE"
    LOG_DIR = os.path.join(settings.PROJECT_DIR, 'logs', 'deploy')
    BUILD_FILE_DIR = '/deploy/'
    DEPLOY_FILE_DIR = '/deploy/'
    DEST_FILE_DIR = '/data/'

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
    build_file_path = models.CharField(max_length=1024, null=True)
    deploy_file_path = models.CharField(max_length=1024, null=True)
    dest_file_path = models.CharField(max_length=1024, null=True)
    backup_file_path = models.CharField(max_length=1024, null=True)
    published_status = models.BooleanField(default=True)

    def __str__(self):
        return self.app_name


class DeployVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    app_name = models.ForeignKey(DeployList, on_delete=models.PROTECT, null=True, verbose_name=_("App Name"))
    version_path = models.CharField(max_length=1024, null=True)
    symbol = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_success_build_num = models.IntegerField(null=True)


def get_deploy_file_path(app_name):
    app = DeployList.objects.get(app_name=app_name)
    return app.deploy_file_path


def get_dest_file_path(app_name):
    fpath, fname = os.path.split(get_deploy_file_path(app_name))
    return os.path.join(DeployList.DEST_FILE_DIR, fname)


def get_remote_data_path(app_name):
    return os.path.join(DeployList.DEST_FILE_DIR, app_name, app_name+'.jar')


def create_or_update(queryset):
    for job in queryset:
        if DeployList.objects.filter(app_name=job['name']):
            data = JenkinsWork().collect_job(name=job['name'])
            task = DeployList.objects.filter(app_name=job['name'])
            if data.get('last_success_build_num', None) is None:
                last_success_build_num = 0
            else:
                last_success_build_num = data.get('last_success_build_num')
            task.update(
                build_status=data.get('build_status', 'RUNNING'),
                last_build_time=data.get('last_build_time', None),
                build_console_output=data.get('build_console_output', ''),
                last_success_build_num=last_success_build_num,
                last_build_num=data.get('last_build_num', None),
                build_file_path=os.path.join(
                    DeployList.BUILD_FILE_DIR,
                    job['name'],
                    'jar',
                    job['name']+str(last_success_build_num)+'.jar'
                )
            )
        else:
            data = JenkinsWork().collect_job(name=job['name'])
            if data.get('last_success_build_num', None) is None:
                last_success_build_num = 0
            else:
                last_success_build_num = data.get('last_success_build_num')
            os.makedirs(os.path.join(DeployList.DEPLOY_FILE_DIR, job['name'], 'jar'), mode=0o755)
            DeployList.objects.create(
                app_name=data['app_name'],
                build_status=data.get('build_status', 'RUNNING'),
                last_build_time=data.get('last_build_time', None),
                build_console_output=data.get('build_console_output', ''),
                last_success_build_num=last_success_build_num,
                last_build_num=data.get('last_build_num', None),
                build_file_path=os.path.join(
                    DeployList.BUILD_FILE_DIR,
                    job['name'],
                    'jar',
                    job['name']+str(last_success_build_num)+'.jar'
                )
            )


def turn_build_file_to_deploy(app_name):
    app = DeployList.objects.get(app_name=app_name)

    src_file = app.build_file_path
    dep_file = os.path.join(
        DeployList.DEPLOY_FILE_DIR,
        app_name,
        'jar',
        app_name+datetime.strftime(datetime.now(), "%Y%m%d%H%M")+'.jar'
    )
    if os.path.isfile(src_file):
        shutil.copyfile(src_file, dep_file)
        app.deploy_file_path = dep_file
        app.save()
        return True
    else:
        return False


def add_version_list(app_name):
    app = DeployList.objects.get(app_name=app_name)
    dl = DeployVersion.objects.filter(app_name=app.id)
    dl.update(symbol=False)

    DeployVersion.objects.create(
        app_name=app,
        version_path=app.deploy_file_path,
        symbol=True,
        last_success_build_num=app.last_success_build_num
    )
