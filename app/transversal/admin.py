from django import forms
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.postgres import fields
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from prettyjson import PrettyJSONWidget
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

from helpers.constants import PARAMETER_TYPE, DEFAULT_READONLY_FIELDS
from app.transversal.models import *

from app.transversal.forms import (
	PerfilAdminForm,
	ParametroAdminForm)


admin.site.unregister(User)
admin.site.unregister(Group)

try:
	admin.site.unregister(StaticDevice)
except NotRegistered:
	pass

try:
	admin.site.unregister(TOTPDevice)

	@admin.register(TOTPDevice)
	class TOTPDeviceCustomAdmin(TOTPDeviceAdmin):

		def has_add_permission(self, request, obj=None):
			return bool(request.user and request.user.username == 'admin')

		def has_change_permission(self, request, obj=None):
			return bool(request.user and request.user.username == 'admin')

		def has_delete_permission(self, request, obj=None):
			return bool(request.user and request.user.username == 'admin')

except NotRegistered:
	pass


class TwoFactorDeviceInline(admin.StackedInline):
	model = TwoFactorDevice
	extra = 0
	max_num = 1
	can_delete = False

	readonly_fields = ('method', 'confirmed', 'key', 'throttling_failure_timestamp', 'throttling_failure_count')
	exclude = ('name',)


class PerfilInline(admin.StackedInline):
	form = PerfilAdminForm
	model = Perfil

	readonly_fields = ('created', 'modified', 'usuario_auth', 'usuario_push')
	exclude = ('two_factor',)


class PerfilAdmin(UserAdmin):
	inlines = [PerfilInline, TwoFactorDeviceInline]

	date_hierarchy = 'date_joined'
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_active',)
	search_fields = (
		'username', 'email', 'first_name', 'last_name', 'perfil__usuario_auth', 'perfil__usuario_push', 'perfil__run')

	def get_queryset(self, request):
		qs = super(PerfilAdmin, self).get_queryset(request)
		if request.user.id == 1:
			return qs
		return qs.exclude(pk=1)

	def formfield_for_dbfield(self, db_field, **kwargs):
		field = super(PerfilAdmin, self).formfield_for_dbfield(db_field, **kwargs)
		user = kwargs['request'].user
		# If not superuser exclude delete permission assignes only admin delete permission
		if not user.is_superuser:
			if db_field.name == 'user_permissions':
				permissions_valid_ids = list()
				for permission in field.queryset.all():
					if 'can_' in permission.codename:
						permissions_valid_ids.append(permission.id)
					elif 'delete' not in permission.codename:
						permissions_valid_ids.append(permission.id)
				field.queryset = field.queryset.filter(id__in=permissions_valid_ids)

		return field

	def get_form(self, request, obj=None, **kwargs):
		form = super(PerfilAdmin, self).get_form(request, obj, **kwargs)

		if not request.user.is_superuser and obj:
			form.base_fields['is_staff'].widget = forms.HiddenInput()
			form.base_fields['is_superuser'].widget = forms.HiddenInput()
		return form


admin.site.register(User, PerfilAdmin)


@admin.register(Group)
class GroupAdmin(GroupAdmin):
	filter_horizontal = ('permissions',)

	def formfield_for_dbfield(self, db_field, **kwargs):
		field = super(GroupAdmin, self).formfield_for_dbfield(db_field, **kwargs)
		user = kwargs['request'].user
		# If not superuser exclude delete permission assignes only admin delete permission
		if not user.is_superuser:
			if db_field.name == 'permissions':
				permissions_valid_ids = list()
				for permission in field.queryset.all():
					if 'can_' in permission.codename:
						permissions_valid_ids.append(permission.id)
					elif 'delete' not in permission.codename:
						permissions_valid_ids.append(permission.id)
				field.queryset = field.queryset.filter(id__in=permissions_valid_ids)

		return field


@admin.register(Parameter)
class ParametroAdmin(admin.ModelAdmin):
	form = ParametroAdminForm
	list_display = ('key', 'get_valor', 'description')
	search_fields = ('key',)
	readonly_fields = ('key', 'description',)
	fieldsets = ((None, {'fields': ('key', 'value', 'description',)}),)

	def has_add_permission(self, request):
		return bool(request.user and request.user.username == 'admin')

	def has_delete_permission(self, request, obj=None):
		return bool(request.user and request.user.username == 'admin')

	def get_valor(self, obj):
		value = obj.value
		if obj.parameter_type == PARAMETER_TYPE['SELECT'] and not obj.parameter_choices:
			if obj.value == '1':
				value = _('Si')
			else:
				value = _('No')

		return value
	get_valor.short_description = _('Valor')


@admin.register(TemplateNotification)
class TemplateNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'reason', 'mail_provider')
    list_filter = ('reason', )

    fieldsets = (
        (None, {'fields': ('name', 'reason')}),
        (_('Template Email'), {'fields': ('mail_provider', 'html')}),
    )

    class Media:
        js = (
            'https://cdn.tiny.cloud/1/0ydr7hcqrewkhn65gvxb17l0uxzmp7d87ko1dtlvgipeyilx/tinymce/5/tinymce.min.js',
            '/static/js/vendor/textareas_tinycloud5.js'
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','subject', 'template', 'destination', 'created')
    search_fields = ('subject', 'context')
    list_filter = ('is_read', )


@admin.register(NotificationEmail)
class NotificationEmailAdmin(admin.ModelAdmin):
    list_display = ('notification', 'is_send', 'created')
    list_filter = ('is_send', )
    date_hierarchy = 'created'
    raw_id_fields = ['notification']


class NotificationMailProviderParamInline(admin.TabularInline):
    fieldsets = (
        (None, {'fields': ('key', 'value')}),
    )
    model = NotificationMailProviderParam
    extra = 0


@admin.register(NotificationMailProvider)
class NotificationMailProviderAdmin(admin.ModelAdmin):
    inlines = [NotificationMailProviderParamInline]
    list_display = ('name', 'is_active', 'is_principal', 'integration')


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
	readonly_fields = DEFAULT_READONLY_FIELDS

