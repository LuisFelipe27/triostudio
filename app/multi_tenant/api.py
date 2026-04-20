from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from app.multi_tenant.models import Tenant
from app.multi_tenant.serializers import TenantSerializer
from config.config import ENVIRONMENT
from helpers.decorators.api import api_authenticate
from helpers.functions.utils import get_subdomain
from helpers.middleware.rest_framwork_fix import SessionAuthenticationAnonymous

import requests
import json


class CsrfExemptSessionAuthentication(SessionAuthentication):
	def enforce_csrf(self, request):
		return  # Remove el chequeo del CSRF


class TenantViewset(viewsets.ModelViewSet):
	authentication_classes = (CsrfExemptSessionAuthentication, )
	queryset = Tenant.objects.all()
	serializer_class = TenantSerializer

	@action(detail=True, methods=['get'], url_path='status-client-process-create')
	def status_client_process_create(self, request, pk=None):
		client = Tenant.objects.get(id=pk)
		return Response({'status': client.is_finish_process, 'observations': client.observations_finish_process})

	@action(detail=True, methods=['get'], url_path='validaurl')
	def valida_url(self, request):
		clientes = Tenant.objects.all()
		for cliente in clientes:
			pass
			# cliente.url
		return Response({'status': 'st'})

	@action(detail=False, methods=['get'], url_path='ruta')
	def valida_ruta(self, request):
		dominio = request.GET['dominio']

		subdominio = get_subdomain(dominio)

		dominio_url = '%s.ordenadito.cl' % subdominio

		ruta_ocupada = ''
		i = 1
		status = 'disponible'
		dominio_new = ''
		while i < 1000:
			clientes = Tenant.objects.filter(domain_url=dominio_url)
			if clientes.exists():
				status = 'sugerir'
				ruta_ocupada = dominio
				dominio_new = '%s-%s' % (dominio, str(i))
				subdominio = get_subdomain(dominio_new)
				dominio_url = f'{subdominio}.ordenadito.cl'
				i += 1
			else:
				i = 1000
				return Response({'status': 'disponible', 'ruta': dominio_new, 'ruta_ocupada': ruta_ocupada})

		return Response({'status': 'true'})

	@action(detail=False, methods=['get'], url_path='geoip', permission_classes=[AllowAny], authentication_classes=[SessionAuthenticationAnonymous])
	@api_authenticate()
	def geoip(self, request):
		def get_client_ip(request):
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]
			else:
				ip = request.META.get('REMOTE_ADDR')
			return ip

		api_url = 'http://www.geoplugin.net/json.gp?ip={}'.format(get_client_ip(request))
		response = requests.get(api_url, verify=False) # verify SSL

		try:
			return Response(json.loads(response.text))
		except Exception as e:
			return Response({'status': False, 'message': 'Error api query'})