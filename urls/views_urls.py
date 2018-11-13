from django.urls import path

from .. import views

app_name = 'deploy'


urlpatterns = [
    path('', views.DeployIndex.as_view(), name='deploy_list')
]