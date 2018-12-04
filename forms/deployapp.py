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
        fields = ['app_name', 'bound_asset']
        widgets = {
            'bound_asset': forms.SelectMultiple(attrs={
                'class': 'select2', 'data-placeholder': _('bound_asset')
            }),
        }
        labels = {}
        help_texts = {}
