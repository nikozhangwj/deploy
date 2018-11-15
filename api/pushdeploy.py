# encoding: utf-8

from django.db import transaction
from rest_framework import generics
from rest_framework.response import Response
from ..models import DeployList

"""
class PushDeployToAsset(generics.RetrieveAPIView):

    queryset = DeployList.objects.all()

    def retrieve(self, request, *args, **kwargs):
        admin_user = self.get_object()
        print(admin_user)
        return Response({"task": admin_user})
"""