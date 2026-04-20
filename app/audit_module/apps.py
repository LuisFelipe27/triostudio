from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditModuleConfig(AppConfig):
    name = 'app.audit_module'
    verbose_name = _('Módulo de Auditoría')
