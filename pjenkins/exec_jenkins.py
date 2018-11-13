import jenkins

username = 'admin'
password = 'admin'
server = jenkins.Jenkins('http://10.128.1.249:8080/login?from=%2F', username=username, password=password)


def collect_all_job():
    all_job = server.get_all_jobs()
    print(all_job)
    return all_job
