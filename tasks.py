#  encoding: utf-8
import json
import re
import os

from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import ugettext as _
# from assets.models import AdminUser, Asset
from .models import get_deploy_file_path, get_remote_data_path, get_version, get_deploy_jar_path
from . import const

CREATE_PROJECT_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'create_project_dir.sh')
CHOWN_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'chown.sh')
COMPRESS_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'compress_tar.sh')

# just for test #
@shared_task
def test_ansible_ping(asset):
    task_name = _("test ansible ping {}".format(asset.hostname))
    return test_ansible_ping_util(asset, task_name)


@shared_task
def test_ansible_ping_util(asset, task_name):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset.fullname]
    tasks = const.TEST_CONN_TASKS
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result, summery = task.run()
    return result


# deploy check file exist #
@shared_task
def check_asset_file_exist(asset, app_name):
    task_name = _("check {0} {1} exist".format(asset, app_name))
    return check_asset_file_exist_util(asset, app_name, task_name)


@shared_task
def check_asset_file_exist_util(asset, app_name, task_name):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset.fullname]
    tasks = const.CHECK_FILE_TASK
    tasks[0]['action']['args'] = "ls -la /data/{}".format(app_name)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result


# deploy function #
@shared_task
def push_build_file_to_asset_manual(asset, app_name):
    task_name = _("push {0} build file to {1}".format(app_name, asset.hostname))
    return push_build_file_to_asset_util(asset, task_name, app_name)


@shared_task
def push_build_file_to_asset_util(asset, task_name, app_name):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset.fullname]
    tasks = const.COPY_FILE_TO_TASK
    tasks[0]['action']['args'] = "creates=/data/{0} {1} {2}".format(app_name, CREATE_PROJECT_SCRIPT_DIR, app_name)
    tasks[1]['action']['args'] = "src={0} dest={1}".format(
        get_deploy_file_path(app_name),
        get_deploy_file_path(app_name)
    )
    tasks[2]['action']['args'] = "path={0} state=absent".format(get_remote_data_path(app_name))
    tasks[3]['action']['args'] = "{0} {1} {2}".format(COMPRESS_SCRIPT_DIR, app_name, get_version(app_name))
    tasks[4]['action']['args'] = "src={0} state=link path={1}".format(
        get_deploy_jar_path(app_name),
        get_remote_data_path(app_name)
    )
    tasks[5]['action']['args'] = "{0} {1}".format(CHOWN_SCRIPT_DIR, app_name)
    tasks[6]['action']['args'] = "/etc/init.d/APP {0} {1}".format('stop', app_name)
    tasks[7]['action']['args'] = "/etc/init.d/APP {0} {1}".format('start', app_name)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result
