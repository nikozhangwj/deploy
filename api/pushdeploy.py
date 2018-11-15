# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from ..models import DeployList
from assets.models import AdminUser
from django.http import JsonResponse


def get_host_admin(request):
    print(request.GET)
    return JsonResponse(dict(code=200))
