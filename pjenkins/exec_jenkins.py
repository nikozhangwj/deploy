import jenkins
from django.utils.timezone import datetime


class JenkinsWork(object):

    def __init__(self):
        self.username = 'admin'
        self.password = 'admin'
        self.server = jenkins.Jenkins(
            'http://192.168.0.124:8081/login?from=%2F', username=self.username, password=self.password
        )

    def collect_all_job(self):
        all_job = self.server.get_all_jobs()
        return all_job

    def collect_job(self, name):
        job = self.server.get_job_info(name=name)
        try:
            last_success_build_num = job['lastSuccessfulBuild']['number']
        except BaseException as error:
            last_success_build_num = None

        try:
            last_build_num = job['lastBuild']['number']
        except BaseException as error:
            return False

        last_build_info = self.server.get_build_info(name, last_build_num)
        last_build_console = self.server.get_build_console_output(name, last_build_num)
        last_build_status = last_build_info['result']

        ts = last_build_info['timestamp']
        sp = float(str(ts)[0:-3] + '.' + str(ts)[-3:])
        last_build_time = datetime.strftime(datetime.fromtimestamp(sp), "%Y-%m-%d %H:%M:%S")

        return {
            'app_name': name,
            'build_status': last_build_status,
            'last_build_time': last_build_time,
            'build_console_output': last_build_console,
            'last_success_build_num': last_success_build_num
        }

    def build_job(self, name):
        print(name)
        return dict(code=200)
