# -*- encoding: utf-8 -*-
from datetime import datetime, date, timedelta, time
from django import forms
from django.core.exceptions import ValidationError
from app.multi_tenant.models import ConfigTenant


class ConfigTenantAdminForm(forms.ModelForm):
	class Meta:
		model = ConfigTenant
		fields = '__all__'

	def clean(self):
		cleaned_data = self.cleaned_data
		if cleaned_data.get('es_repositorio'):
			if bool( ConfigTenant.objects.filter(es_repositorio=True).exclude(pk=self.instance.id) ):
				raise forms.ValidationError("Ya existe un tenant como repositorio.")

		return cleaned_data
