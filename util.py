# encoding: utf-8
from .models.deploy_list import *
import tarfile


def pack_up_deploy_file(asset, app_name, only_jar=True):
    if only_jar:
        exclude_names = []
    else:
        exclude_names = []