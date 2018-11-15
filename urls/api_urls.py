from django.urls import path

from .. import views
from ..api import pushdeploy

app_name = 'deploy'

urlpatterns = [
    path('get_jenkins_all/', views.get_jenkins_all, name='get_jenkins_all'),
    path('build_app/', views.build_app, name='build_app'),
    path('get_host_admin/', pushdeploy.get_host_admin, name='get_host_admin'),
]
