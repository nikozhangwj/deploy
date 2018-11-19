# encoding: utf-8
import os
import shutil
from datetime import datetime
from .models import DeployList


def turn_build_file_to_deploy(app_name):
    app = DeployList.objects.get(app_name=app_name)

    src_file = app.build_file_path
    dep_file = os.path.join(
        DeployList.DEPLOY_FILE_DIR,
        app_name,
        app_name+datetime.strftime(datetime.now(), "%Y%m%d%H%M")+'.jar'
    )
    if os.path.isfile(src_file):
        shutil.copyfile(src_file, dep_file)
        app.deploy_file_path = dep_file
        app.save()
        return True
    else:
        return False
