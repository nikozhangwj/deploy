# -*- coding: utf-8 -*-
#
import uuid
import os
import shutil
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
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
    BACKUP_DIR = '/deploy/{0}/bak/'
    BACKUP_FILE_DIR = '{APP_NAME}_backup_{VERSION}/{APP_NAME}_full_backup_{VERSION}.tar.gz'
    BACKUP_DIRECTORY_DIR = '/deploy/{APP_NAME}/bak/{APP_NAME}_backup_{VERSION}/'

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
    bound_asset = models.ManyToManyField('assets.Asset', blank=True, verbose_name=_("Assets"))

    def __str__(self):
        return self.app_name


class DeployVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    app_name = models.ForeignKey(DeployList, on_delete=models.PROTECT, null=True, verbose_name=_("App Name"))
    version_path = models.CharField(max_length=1024, null=True)
    symbol = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    last_success_build_num = models.IntegerField(null=True)
    version_status = models.BooleanField(default=True)
    version = models.CharField(max_length=1024, null=True)
    backup_file_path = models.CharField(max_length=1024, null=True)


def get_deploy_file_path(app_name):
    app = DeployList.objects.get(app_name=app_name)
    return app.deploy_file_path + '.tar.gz'


def get_deploy_jar_path(app_name):
    app = DeployList.objects.get(app_name=app_name)
    return os.path.join(app.deploy_file_path, app_name+'.jar')


def get_dest_file_path(app_name):
    fpath, fname = os.path.split(get_deploy_file_path(app_name))
    return os.path.join(DeployList.DEST_FILE_DIR, fname)


def get_remote_data_path(app_name):
    return os.path.join(DeployList.DEST_FILE_DIR, app_name, app_name+'.jar')


def get_version(app_name):
    app = DeployList.objects.get(app_name=app_name)
    deploy_file_path = app.deploy_file_path
    return deploy_file_path.split('/')[-1]


def get_version_path(app_name, version):
    app = DeployList.objects.get(app_name=app_name)
    v = DeployVersion.objects.get(app_name=app.id, version=version)
    return v.version_path


def get_last_version(app_name):
    app = DeployList.objects.get(app_name=app_name)
    version_path = DeployVersion.objects.filter(app_name_id=app.id, symbol=True)
    try:
        version = version_path[0].version_path.split('/')[-1]
    except BaseException as error:
        return False
    return version


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
                    'app',
                    job['name']+str(last_success_build_num)
                )
            )
        else:
            data = JenkinsWork().collect_job(name=job['name'])
            if data.get('last_success_build_num', None) is None:
                last_success_build_num = 0
            else:
                last_success_build_num = data.get('last_success_build_num')
            os.makedirs(os.path.join(DeployList.DEPLOY_FILE_DIR, job['name'], 'app'), mode=0o755)
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
                    'app',
                    job['name']+str(last_success_build_num)
                )
            )


def is_same_build(app_name):
    app = DeployList.objects.get(app_name=app_name)
    version = DeployVersion.objects.filter(app_name=app.id, symbol=True).order_by('-create_time')[:1]
    if version[0].last_success_build_num == app.last_success_build_num:
        return True
    elif version[0].last_success_build_num != app.last_success_build_num:
        return False
    else:
        return False


def turn_build_file_to_deploy(app_name):
    app = DeployList.objects.get(app_name=app_name)

    if is_same_build(app_name):
        return True

    src_file = app.build_file_path
    dep_file = os.path.join(
        DeployList.DEPLOY_FILE_DIR,
        app_name,
        'app',
        app_name+datetime.strftime(datetime.now(), "%Y%m%d%H%M")
    )
    if os.path.isdir(src_file):
        shutil.copytree(src_file, dep_file)
        app.deploy_file_path = dep_file
        app.save()
        return True
    else:
        return False


def add_version_list(app_name, version_status=True):
    app = DeployList.objects.get(app_name=app_name)
    dl = DeployVersion.objects.filter(app_name=app.id)
    dl.update(symbol=False)

    try:
        version = DeployVersion.objects.get(version_path=app.deploy_file_path)
        version.version_status = version_status
        version.symbol = True
        version.save()
        return True
    except BaseException as error:
        print(error)
        pass

    DeployVersion.objects.create(
        app_name=app,
        version_path=app.deploy_file_path,
        symbol=True,
        last_success_build_num=app.last_success_build_num,
        version_status=version_status,
        version=app.deploy_file_path.split('/')[-1],
        backup_file_path=os.path.join(
            DeployList.BACKUP_DIR.format(app_name),
            DeployList.BACKUP_FILE_DIR.format(APP_NAME=app_name, VERSION=app.deploy_file_path.split('/')[-1])
        )
    )


def save_backup_path(app_name, version):
    try:
        app = DeployList.objects.get(app_name=app_name)
    except BaseException as error:
        return False
    app.backup_file_path = os.path.join(
        DeployList.BACKUP_DIR.format(app_name),
        DeployList.BACKUP_FILE_DIR.format(APP_NAME=app_name, VERSION=version)
    )
    app.save()
    return True


def get_app_id(app_name):
    try:
        app = DeployList.objects.get(app_name=app_name)
    except ObjectDoesNotExist as error:
        return False
    return app.id


def get_backup_path(app_name, version):
    try:
        data = DeployVersion.objects.get(app_name=get_app_id(app_name), version=version)
    except ObjectDoesNotExist as error:
        return error

    return data.backup_file_path


def get_backup_directory(app_name, version):
    return DeployList.BACKUP_DIRECTORY_DIR.format(APP_NAME=app_name, VERSION=version)


def change_version_active(app_name, version):
    try:
        app = DeployList.objects.get(app_name=app_name)
    except ObjectDoesNotExist as error:
        print(error)
        return False
    dl = DeployVersion.objects.filter(app_name=app.id)
    dl.update(symbol=False)
    try:
        d_version = DeployVersion.objects.get(app_name=app.id, version=version)
    except ObjectDoesNotExist as error:
        print(error)
        return False
    d_version.symbol = True
    d_version.save()
    return True
