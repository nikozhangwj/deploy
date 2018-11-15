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
    job_id = request.GET.get('id')
    try:
        job = DeployList.objects.get(id=job_id)
    except BaseException as error:
        return JsonResponse(dict(code=400, error='error'))
    JenkinsWork().build_job(job.app_name)
    return JsonResponse(dict(code=200, mgs='success'))


class DeployOptionList(DetailView):
    model = DeployList
    template_name = 'deploy/deploy_detail.html'
    context_object_name = 'result'
