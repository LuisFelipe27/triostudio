# -*- coding: utf-8 -*-
from rest_framework.exceptions import AuthenticationFailed

def api_authenticate():
	def real_decorator(function):
		
		def wrap(request, *args, **kwargs):

			if 'api_key' in args[0].query_params and args[0].query_params['api_key'] == 'NTNjMDIxYWMtNTE1MS00YjRkLThjNzgtMGVjZDI4N2JhYmJh':
				return function(request, *args, **kwargs)

			else:
				raise AuthenticationFailed(detail='api key incorrect or not supplied')
			
		wrap.__doc__ = function.__doc__
		wrap.__name__ = function.__name__
		return wrap

	return real_decorator
