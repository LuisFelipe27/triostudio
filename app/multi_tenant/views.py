# -*- encoding: utf-8 -*-
from django.db import connection

from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from app.multi_tenant.models import Tenant
from django.utils.translation import gettext_lazy as _

from config.config import (
	ENVIRONMENT, CLOUDFLARE_API_URL, CLOUDFLARE_ZONE_IDENTIFIER,
	CLOUDFLARE_TOKEN
)
import requests

from helpers.functions.utils import get_subdomain


@login_required
def index(request):
	tenants = Tenant.objects.exclude(schema_name='public')
	context = {'tenants': tenants, 'section': _('Clientes')}
	return render(request, 'multi_tenant/index.html', context)


@login_required
def modal_create_client(request):
	if request.POST:
		domain = request.POST.get('dominio')
		schema = f'tenant_{str(domain).replace("-", "_")}'

		subdominio = get_subdomain(domain)

		dominio_url = '%s.ordenadito.cl' % subdominio

		email = request.POST['email']
		password = request.POST['password']
		nombre_usuario = email.split('@')[0]

		tenant = Tenant(
			domain_url=dominio_url,
			schema_name=schema,
			name=request.POST['nombre_negocio']
		)
		tenant.save()

		# CREATE DNS IN CLOUDFLARE
		if CLOUDFLARE_TOKEN and CLOUDFLARE_API_URL and CLOUDFLARE_ZONE_IDENTIFIER:
			headers = {
				'Authorization': f'Bearer {CLOUDFLARE_TOKEN}',
				'Content-Type': 'application/json'
			}
			url = f'{CLOUDFLARE_API_URL}/zones/{CLOUDFLARE_ZONE_IDENTIFIER}/dns_records'
			data = {
				'type': 'A',
				'name': f'{dominio_url}',
				'content': f"{ENVIRONMENT['IP']}",
				'ttl': 3600,
				'priority': 10,
				'proxied': True
			}

			result = requests.post(url, headers=headers, json=data)
			response = result.json()
			if True:
				tenant.id_dns_cloudflare = response['result']['id']
				tenant.save()
				messages.add_message(request, messages.SUCCESS, _('Cliente creado correctamente.'))
			else:
				tenant.delete()
				messages.add_message(request, messages.ERROR, _('Error al crear cliente.'))

		connection.schema_name = schema

		User.objects.create_superuser(
			'admin', 'lvergara23@gmail.com', 'h1OiJvAOcAacfRGcE4E3'
		)
		User.objects.create_superuser(nombre_usuario, email, password)

		# Load Fixtures
		call_command('loaddata', 'groups.json')
		call_command('loaddata', 'endpoints.json')

		connection.schema_name = 'public'

		return HttpResponseRedirect('/')

	context = {'enviroment_name': ENVIRONMENT['name']}
	return render(request, 'multi_tenant/modals/modal_create_client.html', context)
