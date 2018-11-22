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
        "name": "script",
        "action": {
            "module": "script",
            "args": ""
        }
    },
    {
        "name": "copy",
        "action": {
            "module": "copy",
            "args": ""
        }
    },
    {
        "name": "file",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "file",
        "action": {
            "module": "file",
            "args": "",
        }
    },
    {
        "name": "shell",
        "action": {
            "module": "shell",
            "args": "",
        }
    },
    {
        "name": "shell",
        "action": {
            "module": "shell",
            "args": "",
        }
    },
    {
        "name": "shell",
        "action": {
            "module": "shell",
            "args": "",
        }
    }
]
