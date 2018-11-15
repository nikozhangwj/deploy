from django.urls import path

from .. import views
# from ..api import pushdeploy

app_name = 'deploy'

urlpatterns = [
    path('get_jenkins_all/', views.get_jenkins_all, name='get_jenkins_all'),
    path('build_app/', views.build_app, name='build_app'),
    # path('deploy_app/', views.deploy_app, name='deploy_app'),

    # path('deploy_app/<uuid:pk>/to_asset/',
         # pushdeploy.PushDeployToAsset.as_view(), name='deploy_app_to_asset'),
]
