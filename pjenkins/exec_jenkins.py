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
        return job
