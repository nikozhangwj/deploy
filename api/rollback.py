# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from django.utils import timezone
from django.core import serializers
from ..models import DeployList, DeployVersion, add_version_list, turn_build_file_to_deploy
from assets.models import AdminUser, Asset
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from ..tasks import rollback_asset_app_version_manual, rollback_check_backup_file_exist


def rollback(request):
    task_host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(id=task_host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    version = request.GET.get('version')
    app_name = request.GET.get('app_name')

    # check target version backup file exist
    exist_result = rollback_check_backup_file_exist(asset, app_name, version)
    if exist_result == 'not':
        return JsonResponse(dict(code=400, error='备份文件'+version+'不存在'))
    if not exist_result:
        return JsonResponse(dict(code=400, error='unknown error'))

    result = rollback_asset_app_version_manual(asset, app_name, version)

    print(result)

    if result[0]['failed']:
        return JsonResponse(dict(code=400, error=str(result[0]['failed'])))

    return JsonResponse(dict(code=200, msg=str(result)))
