# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields.array import ArrayField
from django.utils.translation import gettext_lazy as _
from colorfield.fields import ColorField
from tenant_schemas.models import TenantMixin

from helpers.functions.utils import tenant_current
from helpers.functions.validators import validate_file_extension_odt, validate_file_extension_img, validate_file_extension
from helpers.classes.storage import LocalMediaStorage
from helpers.constants import PARAMETER_TYPE, PARAMETERS_TYPES


class Tenant(TenantMixin):
	name = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)
	is_principal = models.BooleanField(default=True)
	id_dns_cloudflare = models.TextField(default='', blank=True)

	# default true, schema will be automatically created and synced when it is saved
	auto_create_schema = True

	def __str__(self):
		return f'{self.name}'


class ConfigTenant(models.Model):
	tenant = models.OneToOneField('multi_tenant.Tenant', models.CASCADE)
	expiracion = models.DateField(blank=True, null=True)

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Configuracion de Cliente"
		verbose_name_plural = "Configuracion de Clientes"

	def __str__(self):
		return '%s' % (self.tenant.name)


class Tour(models.Model):
	codigo = models.CharField(max_length=100)
	nombre = models.CharField(max_length=100)

	class Meta:
		verbose_name = 'Tour'
		verbose_name_plural = 'Tours'

	def __str__(self):
		return self.nombre
