#  encoding: utf-8
import json
import re
import os

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext as _
from common.utils import get_logger
# from assets.models import AdminUser, Asset
from .models import get_deploy_file_path, get_remote_data_path, get_version, get_deploy_jar_path, get_last_version, \
    save_backup_path, get_backup_path, get_version_path, get_backup_directory, update_deploy_info
from . import const

CREATE_PROJECT_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'create_project_dir.sh')
CHOWN_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'chown.sh')
COMPRESS_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'compress_tar.sh')
BACKUP_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'backup.sh')
UNPACK_SCRIPT_DIR = os.path.join(settings.BASE_DIR, 'deploy', 'script', 'unpack.sh')


logger = get_logger('jumpserver')


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
    task_name = _("check {0} {1} exist {2}".format(asset, app_name, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return check_asset_file_exist_util(asset, app_name, task_name)


@shared_task
def check_asset_file_exist_util(asset, app_name, task_name):
    from ops.utils import update_or_create_ansible_task
    logger.info('检查{0}是否已存在{1}应用文件'.format(asset.hostname, app_name))
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
    task_name = _("push {0} build file to {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
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


# backup function #
@shared_task
def backup_asset_app_file(asset, app_name):
    task_name = _("backup {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return backup_asset_app_file_util(asset, task_name, app_name)


@shared_task
def backup_asset_app_file_util(asset, task_name, app_name):
    from ops.utils import update_or_create_ansible_task
    version = get_last_version(app_name)
    if not version:
        logger.info("no version history found {0}".format(app_name))
        return False
    hosts = [asset.fullname]
    tasks = const.BACKUP_FILE
    tasks[0]['action']['args'] = "{0} {1} {2}".format(BACKUP_SCRIPT_DIR, app_name, version)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    if result[1]['dark']:
        logger.info('{0} Backup Failed! {1}'.format(app_name, result[1]['dark']))
        return result[1]['dark']

    if not save_backup_path(app_name, version):
        return False
    logger.info('{0} backup complete.'.format(version))

    return result


# rollback version
def rollback_asset_app_version_manual(asset, app_name, version):
    task_name = _("backup {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return rollback_asset_app_version_util(asset, task_name, app_name, version)


def rollback_asset_app_version_util(asset, task_name, app_name, version):
    from ops.utils import update_or_create_ansible_task

    hosts = [asset.fullname]
    tasks = const.ROLLBACK_TASK
    # unpack
    tasks[0]['action']['args'] = "{0} {1} {2} {3}".format(
        UNPACK_SCRIPT_DIR,
        get_backup_path(app_name, version),
        get_backup_directory(app_name, version),
        app_name
    )

    # remove link
    tasks[1]['action']['args'] = "path={0} state=absent".format(get_remote_data_path(app_name))
    # create new link
    tasks[2]['action']['args'] = "src={0} state=link path={1}".format(
        os.path.join(get_version_path(app_name, version), app_name+'.jar'),
        get_remote_data_path(app_name)
    )

    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()
    deploy_file_path = get_version_path(app_name, version)
    if result[0]['ok']:
        update_deploy_info(app_name, deploy_file_path)

    # logger.info(result[0]['ok'])
    return result


# rollback check backupfile exist
def rollback_check_backup_file_exist(asset, app_name, version):
    task_name = _("backup {0} on {1} {2}".format(app_name, asset.hostname, timezone.localtime().strftime("[%Y-%m-%d %H:%M:%S]")))
    return rollback_check_backup_file_exist_util(asset, task_name, app_name, version)


def rollback_check_backup_file_exist_util(asset, task_name, app_name, version):
    from ops.utils import update_or_create_ansible_task
    simple_result = None
    backup_path = get_backup_path(app_name, version)
    if not backup_path:
        return False
    tasks = const.CHECK_FILE_TASK
    hosts = [asset.fullname]
    tasks[0]['action']['args'] = "if [ -f '{0}' ]; then echo 'exist'; else echo 'not'; fi".format(backup_path)
    print(tasks)
    task, create = update_or_create_ansible_task(
        task_name=task_name,
        hosts=hosts, tasks=tasks,
        pattern='all',
        options=const.TASK_OPTIONS, run_as_admin=True, created_by='System'
    )

    result = task.run()

    if result[1]['dark']:
        logger.error(result[1]['dark'])
        return False
    if result[0]['ok']:
        simple_result = result[0]['ok'][asset.fullname]['CHECK_FILE_EXIST']['stdout']

    logger.info(simple_result)

    return simple_result
