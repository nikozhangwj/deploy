from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from .pjenkins.exec_jenkins import JenkinsWork
# Create your views here.
from .models.deploy_list import DeployList, create_or_update


class DeployIndex(ListView):
    model = DeployList
    template_name = 'deploy/deploy_list.html'
    context_object_name = 'deploys'


def get_jenkins_all(request):
    jobs = JenkinsWork().collect_all_job()
    create_or_update(jobs)
    return JsonResponse(dict(code=200))


def build_app(request):
    print('build')
    return JsonResponse(dict(code=200))
