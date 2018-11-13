from django.shortcuts import render
from django.http import JsonResponse
from .models.deploy_list import DeployList
from django.views.generic import ListView, DetailView
# Create your views here.


class DeployIndex(ListView):
    model = DeployList
    template_name = 'deploy/deploy_list.html'
    context_object_name = 'deploys'


def get_jenkins_all(request):
    print('jenkins')
    return JsonResponse(dict(code=200))
