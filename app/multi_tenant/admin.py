# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from app.multi_tenant.forms import ConfigTenantAdminForm
from app.multi_tenant.models import (
	ConfigTenant, Tour
)


@admin.register(ConfigTenant)
class ConfigTenantAdmin(admin.ModelAdmin):
	form = ConfigTenantAdminForm

	list_display = ('id', 'tenant', 'created', 'modified')
	search_fields = ('tenant__name', )
	# readonly_fields = ('steps_configured', )


admin.site.register(Tour)
