from auditlog.models import LogEntry as LogEntryAuditLog
from django.db import models
from django.contrib.admin.models import LogEntry as LogEntryAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from helpers.classes.models import RecordsModel


class AdminLog(LogEntryAdmin):

    class Meta:
        proxy = True
        verbose_name = _("Log de Usuario")
        verbose_name_plural = _("Logs de Administración")


class SystemLog(LogEntryAuditLog):

    class Meta:
        proxy = True
        verbose_name = _("Log de Usuario")
        verbose_name_plural = _("Logs de Sistema")


class DatabaseBackupLog(models.Model):
    event_date = models.DateTimeField(verbose_name=_('Fecha Evento'))
    description = models.TextField(verbose_name=_('Descripción'))

    @property
    def format_chile_event_date(self):
        return self.event_date.strftime('%d-%m-%Y %H:%M:%S')

    class Meta:
        verbose_name = 'Log Respaldo Base de Datos'
        verbose_name_plural = 'Logs Respaldos Base de Datos'

    def __str__(self):
        return "{} | {}".format(self.event_date, self.description)


class RequestLog(RecordsModel):
    remote_address = models.CharField(max_length=100)
    server_hostname = models.CharField(max_length=200)
    domain_url = models.CharField(max_length=200)
    request_method = models.CharField(max_length=100)
    request_path = models.TextField()
    request_body = models.TextField(null=True, blank=True)
    run_time = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Log de Solicitud'
        verbose_name_plural = 'Logs de Solicitudes'


class Permission(models.Model):
    """ This is only to control the permissions of the "audit_module" application.
    """
    class Meta:
        default_permissions = ()
        permissions = ()
