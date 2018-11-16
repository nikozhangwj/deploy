#  encoding: utf-8

TASK_OPTIONS = {
    'timeout': 10,
    'forks': 10,
}

TEST_CONN_TASKS = [
    {
        "name": "ping",
        "action": {
            "module": "ping",
            "args": "",
        }
    }
]

COPY_FILE_TO_TASK = [
    {
        "name": "copy",
        "action": {
            "module": "copy",
            "args": ""
        }
    }
]