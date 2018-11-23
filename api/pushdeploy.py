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
from ..tasks import test_ansible_ping, push_build_file_to_asset_manual, check_asset_file_exist
from ..util import pack_up_deploy_file


def get_host_admin(request):
    print(request.GET)
    host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(ip=host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    task = test_ansible_ping(asset)
    print(task)
    return JsonResponse(dict(code=200, task=task))


def deploy_file_to_asset(request):
    host = request.GET.get('task_host')
    app_name = request.GET.get('app_name')
    try:
        asset = Asset.objects.get(ip=host)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))

    if not turn_build_file_to_deploy(app_name):
        return JsonResponse(dict(code=400, error='file not found!'))

    check_result = check_asset_file_exist(asset, app_name)

    if check_result[0]['ok']:
        pack_up_deploy_file(app_name)
        return JsonResponse(dict(code=200))
    else:
        pack_up_deploy_file(app_name, only_jar=False)
        return JsonResponse(dict(code=400, error='asset file not found!'))

    if not turn_build_file_to_deploy(app_name):
        return JsonResponse(dict(code=400, error='file not found!'))

    task = push_build_file_to_asset_manual(asset, app_name)
    job = DeployList.objects.get(app_name=app_name)
    if task[1]['dark']:
        job.published_status = False
        job.save()
        add_version_list(app_name, version_status=False)
        return JsonResponse(dict(code=400, error=task[1]['dark']))
    elif task[0]['ok']:
        job.published_time = timezone.now()
        job.published_status = True
        job.save()
        add_version_list(app_name)
        return JsonResponse(dict(code=200, task=task))
    else:
        return JsonResponse(dict(code=400, error="升级失败,请回滚"))


def get_version_history(request):
    app_id = request.GET.get('id')
    version = serializers.serialize(
        "json",
        DeployVersion.objects.filter(app_name_id=app_id).order_by('-create_time')[:5]
    )
    print(version)
    return HttpResponse(version)
