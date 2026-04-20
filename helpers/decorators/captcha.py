from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from helpers.functions.captcha import verify_recaptcha_v3
from helpers.constants import RECAPTCHA_V3
import json
import requests


def recaptcha_v3(method, is_api=False):
    def real_decorator(function):

        def wrap(request, *args, **kwargs):
            token, action = None, None
            if is_api:
                if 'captcha_token' in args[0].query_params:
                    token = args[0].query_params['captcha_token']
                if 'captcha_action' in args[0].query_params:
                    action = args[0].query_params['captcha_action']
            else:
                if method == 'POST' and not request.POST:
                    return function(request, *args, **kwargs)

                if method == 'POST':
                    token = request.POST.get('captcha_token')
                    action = request.POST.get('captcha_action')
                else:
                    token = request.GET.get('captcha_token')
                    action = request.GET.get('captcha_action')

            if token and action:
                if verify_recaptcha_v3(token, action):
                    return function(request, *args, **kwargs)
                else:
                    if is_api:
                        return Response({'status': False, 'message': 'reCaptcha no verificado'})
                    else:
                        raise PermissionDenied
            else:
                return function(request, *args, **kwargs)

        wrap.__doc__ = function.__doc__
        wrap.__name__ = function.__name__
        return wrap

    return real_decorator
