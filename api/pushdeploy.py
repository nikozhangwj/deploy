# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from ..models import DeployList
from assets.models import AdminUser, Asset
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from ..tasks import test_ansible_ping


def get_host_admin(request):
    host = request.GET.get('task_host')
    try:
        asset = Asset.objects.get(ip=host)
        print(asset)
    except ObjectDoesNotExist as error:
        return JsonResponse(dict(code=400, error=str(error)))
    task = test_ansible_ping.delay(asset)
    return JsonResponse(dict(code=200, task=task.id))
