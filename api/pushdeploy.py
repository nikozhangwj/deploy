# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from ..models import DeployList
from assets.models import AdminUser, Asset
from django.http import JsonResponse
from ..tasks import test_ansible_ping


def get_host_admin(request):
    host = request.GET.get('task_host')
    asset = Asset.objects.get(ip=host)
    print(asset)
    task = test_ansible_ping.delay(asset)
    print(task)
    print(task.id)
    return JsonResponse(dict(code=200))
