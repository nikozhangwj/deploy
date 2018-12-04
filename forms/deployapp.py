from django import forms
from django.utils.translation import gettext_lazy as _

from common.utils import get_logger
from orgs.mixins import OrgModelForm

from ..models import DeployList, DeployVersion


logger = get_logger(__file__)
__all__ = []


class AppUpdateForm(OrgModelForm):
    class Meta:
        model = DeployList
        fields = ['app_name']
        widgets = {}
        labels = {}
        help_texts = {}
