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
from ..util import pack_up_deploy_file


def rollback(request):
    task_host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(id=task_host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    version = request.GET.get('version')
    app_name = request.GET.get('app_name')

    simple_result = rollback_check_backup_file_exist(asset, app_name, version)
    if simple_result == 'not':
        return JsonResponse(dict(code=400, error=str(simple_result)))
    if not simple_result:
        return JsonResponse(dict(code=400, error='known error'))
    # result = rollback_asset_app_version_manual(asset, app_name, version)

    return JsonResponse(dict(code=200, msg=str(simple_result)))
