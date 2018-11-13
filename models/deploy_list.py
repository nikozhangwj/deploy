# -*- coding: utf-8 -*-
#
import uuid
import os
from django.conf import settings
from django.db import models


class DeployList(models.Model):
    SUCCESS = "success"
    RUNNING = "running"
    FAILED = "failed"
    LOG_DIR = os.path.join(settings.PROJECT_DIR, 'logs', 'deploy')

    STATUS_CHOICES = (
        (SUCCESS, SUCCESS),
        (RUNNING, RUNNING),
        (FAILED, FAILED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    app_name = models.CharField(max_length=1024)
    job_status = models.BooleanField(default=True)
    build_status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    log_path = models.CharField(max_length=256, blank=True, null=True)
    create_time = models.TimeField(auto_now_add=True)
    last_build_time = models.TimeField(null=True)
    build_console_output = models.TextField(blank=True)

    def __str__(self):
        return self.app_name

    def create_or_update(self, queryset):
        pass
