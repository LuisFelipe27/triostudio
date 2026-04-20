from django.contrib.admin.models import LogEntry
from auditlog.models import LogEntry as LogEntryAuditLog
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.fields import Field
from app.audit_module.models import DatabaseBackupLog


class DatabaseBackupLogResource(resources.ModelResource):
    event_date = Field(attribute='format_chile_event_date', column_name=_('Fecha Evento'))
    description = Field(attribute='description', column_name=_('Descripción'))

    class Meta:
        model = DatabaseBackupLog
        exclude = ('id',)


class LogEntryResource(resources.ModelResource):
    object_repr = Field(attribute='object_repr', column_name=_('Objeto'))
    app_label = Field(attribute='content_type__app_label', column_name=_('Módulo'))
    content_type = Field(attribute='content_type__model', column_name=_('Mantenedor'))
    action_flag = Field(attribute='get_action_flag_display', column_name=_('Acción'))
    change_message = Field(attribute='get_change_message', column_name=_('Observación'))
    user = Field(attribute='user__username', column_name=_('Usuario'))
    action_time = Field(attribute='action_time', column_name=_('Fecha y Hora'))

    class Meta:
        model = LogEntry
        exclude = ('id', 'object_id')


class LogEntryAuditLogResource(resources.ModelResource):
    object_repr = Field(attribute='object_repr', column_name=_('Objeto'))
    app_label = Field(attribute='content_type__app_label', column_name=_('Módulo'))
    content_type = Field(attribute='content_type__model', column_name=_('Mantenedor'))
    action_flag = Field(attribute='get_action_display', column_name=_('Acción'))
    change_message = Field(attribute='changes', column_name=_('Observación'))
    user = Field(attribute='actor', column_name=_('Usuario'))
    action_time = Field(attribute='timestamp', column_name=_('Fecha y Hora'))

    class Meta:
        model = LogEntryAuditLog
        exclude = ('id', 'object_pk', 'object_id', 'action', 'changes', 'remote_addr', 'timestamp',
                   'additional_data', 'actor')
