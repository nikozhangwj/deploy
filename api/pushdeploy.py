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
from ..tasks import test_ansible_ping, push_build_file_to_asset_manual


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
    result = turn_build_file_to_deploy(app_name)
    print(result)
    task = push_build_file_to_asset_manual(asset, app_name)
    if task[0]['ok']:
        job = DeployList.objects.get(app_name=app_name)
        job.published_time = timezone.now()
        job.save()
        add_version_list(app_name)
        return JsonResponse(dict(code=200, task=task))
    else:
        return JsonResponse(dict(code=400, error="升级失败,请回滚"))


def get_version_history(request):
    app_id = request.GET.get('id')
    version = serializers.serialize("json", DeployVersion.objects.filter(app_name_id=app_id)).order_by('-create_time')
    print(version)
    return HttpResponse(version)
