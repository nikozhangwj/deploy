from django.urls import path

from .. import views

app_name = 'deploy'

urlpatterns = [
    path('get_jenkins_all/', views.get_jenkins_all, name='get_jenkins_all'),
    path('build_app/', views.build_app, name='build_app'),
]
