# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_text
from django.utils import translation
from helpers.functions.utils import tenant_custom_language, client_has_module as function_client_has_module, \
	language_client


def client_has_module(module_tag):
	def real_decorator(function):

		def wrap(request, *args, **kwargs):
			if function_client_has_module(module_tag):
				return function(request, *args, **kwargs)

			else:
				raise PermissionDenied

		wrap.__doc__ = function.__doc__
		wrap.__name__ = function.__name__
		return wrap

	return real_decorator


def user_has_permissions(groups):
	def real_decorator(function):	
		def wrap(request, *args, **kwargs):
			groups_list = force_text(groups).split(',')

			if bool(User.objects.filter(pk=request.user.id, groups__name__in=groups_list)):
				return function(request, *args, **kwargs)

			else:
				raise PermissionDenied

		wrap.__doc__ = function.__doc__
		wrap.__name__ = function.__name__
		return wrap

	return real_decorator


def translate(func):
	def wrapper(request, *args, **kwargs):
		# Si request viene desde agenda web, o de alguna otra parte donde
		# no sea posible acceder al usuario conectado, se ocupa el lenguaje por defecto
		translation.activate(language_client())
		wrap = func(request, *args, **kwargs)
		return wrap
	return wrapper
