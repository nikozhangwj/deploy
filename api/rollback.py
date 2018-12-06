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
from ..tasks import rollback_asset_app_version_manual
from ..util import pack_up_deploy_file


def rollback(request):
    ip = request.POST.get['ip']
    try:
        asset = Asset.objects.get(ip=ip)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=200, error=str(error)))
    version = request.POST.get['version']
    app_name = request.POST.get['app_name']
    result = rollback_asset_app_version_manual(app_name, version)
    print(result)
    return JsonResponse(dict(code=200, msg=''))
