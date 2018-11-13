from django.urls import path

from .. import views

app_name = 'deploy'


urlpatterns = [
    path('/', views.deploy_list, name='deploy_list')
]