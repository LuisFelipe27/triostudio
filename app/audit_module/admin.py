# -*- encoding: utf-8 -*-
from auditlog.admin import LogEntryAdmin
from auditlog.models import LogEntry
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.translation import ugettext, ugettext_lazy as _
from import_export.admin import ExportMixin, ExportActionModelAdmin
from import_export.formats import base_formats

from app.audit_module.forms import (
    ContentTypeAppLabelAutocompleteFilter,
    ContentTypeModelAutocompleteFilter
)
from app.audit_module.models import AdminLog, SystemLog, DatabaseBackupLog, RequestLog
from app.audit_module.resources import (
    DatabaseBackupLogResource,
    LogEntryResource,
    LogEntryAuditLogResource
)
from helpers.constants import DEFAULT_READONLY_FIELDS

try:
    admin.site.unregister(LogEntry)
except NotRegistered:
    pass


@admin.register(AdminLog)
class AdminLogAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = LogEntryResource
    date_hierarchy = 'action_time'
    search_fields = ('change_message', 'object_repr', 'user__username', 'user__first_name',
                     'user__last_name', 'content_type__model', 'content_type__app_label')
    list_display = ('get_object_display', 'get_app_label', 'get_model', 'action_flag', 'get_change_message', 'user',
                    'action_time')
    list_filter = ('action_flag', 'content_type__app_label', 'content_type__model')
    # list_filter = ('action_flag', ContentTypeAppLabelAutocompleteFilter,
    #                ContentTypeModelAutocompleteFilter)

    list_display_links = None
    list_per_page = 50

    def get_object_display(self, obj):
        try:
            return obj.get_edited_object()
        except Exception:
            return obj.object_repr
    get_object_display.short_description = _('Objeto')

    def get_app_label(self, obj):
        if obj.content_type:
            return obj.content_type.app_label
        else:
            return '--'
    get_app_label.short_description = _('Módulo')

    def get_model(self, obj):
        if obj.content_type:
            return obj.content_type.model
        else:
            return '--'
    get_model.short_description = _('Mantenedor')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return bool(request.user and request.user.username == 'admin')

    def has_change_permission(self, request, obj=None):
        return False

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
              base_formats.CSV,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


@admin.register(SystemLog)
class SystemLogAdmin(ExportActionModelAdmin, LogEntryAdmin):
    resource_class = LogEntryAuditLogResource
    date_hierarchy = 'timestamp'
    list_display = ['id', "resource_url", 'get_app_label', 'get_model', "action", "msg_short", "user_url", "created"]

    def created(self, obj):
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def get_app_label(self, obj):
        if obj.content_type:
            return obj.content_type.app_label
        else:
            return '--'
    get_app_label.short_description = _('Módulo')

    def get_model(self, obj):
        if obj.content_type:
            return obj.content_type.model
        else:
            return '--'
    get_model.short_description = _('Mantenedor')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return bool(request.user and request.user.username == 'admin')

    def has_change_permission(self, request, obj=None):
        return False

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
              base_formats.CSV,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


@admin.register(DatabaseBackupLog)
class DatabaseBackupLogAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = DatabaseBackupLogResource
    date_hierarchy = 'event_date'
    list_display = ('event_date', 'description')

    def has_add_permission(self, request):
        return bool(request.user and request.user.username == 'admin')

    def has_delete_permission(self, request, obj=None):
        return bool(request.user and request.user.username == 'admin')

    def has_change_permission(self, request, obj=None):
        return bool(request.user and request.user.username == 'admin')

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
              base_formats.CSV,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


@admin.register(RequestLog)
class RequestLogAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('request_method', 'created_by')
    list_display = ('request_path', 'domain_url', 'remote_address', 'request_method', 'created_by', 'created')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return bool(request.user and request.user.username == 'admin')

    def has_change_permission(self, request, obj=None):
        return False

    def get_export_formats(self):
        """
        Returns available export formats.
        """
        formats = (
              base_formats.CSV,
              base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]
