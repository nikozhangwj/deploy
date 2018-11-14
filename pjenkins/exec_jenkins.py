import jenkins


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
        last_build_num = job['lastBuild']['number']
        last_success_build_num = job['lastSuccessfulBuild']['number']
        last_build_info = self.server.get_build_info(name, last_build_num)
        last_build_console = self.server.get_build_console_output(name, last_build_num)
        last_build_time = last_build_info['timestamp']
        last_build_status = last_build_info['result']
        return {
            'app_name': name,
            'build_status': last_build_status,
            'last_build_time': last_build_time,
            'build_console_output': last_build_console,
            'last_success_build_num': last_success_build_num
        }
