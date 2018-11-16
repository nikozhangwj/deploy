#  encoding: utf-8
import json
import re
import os

from celery import shared_task
from django.core.cache import cache
from django.utils.translation import ugettext as _
# from assets.models import AdminUser, Asset
from .models import get_deploy_file_path
from . import const


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


# deploy function #
@shared_task
def push_build_file_to_asset_manual(asset, app_name):
    task_name = _("push {0} build file to {1}".format(app_name, asset.hostname))
    return push_build_file_to_asset_util(asset, task_name, app_name)


@shared_task
def push_build_file_to_asset_util(asset, task_name, app_name):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset.fullname]
    tasks = const.COPY_FILE_TO_TASK.format(get_deploy_file_path(app_name), get_deploy_file_path(app_name))

    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    return result
