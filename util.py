# encoding: utf-8
from .models.deploy_list import DeployList
import tarfile


def pack_up_deploy_file(app_name, only_jar=True):
    app = DeployList.objects.get(app_name=app_name)
    deploy_file_path = app.deploy_file_path

    if only_jar:
        exclude_names = []
    else:
        exclude_names = []

