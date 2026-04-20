import requests
import json
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from helpers.constants import ENDPOINT_MODEL_AUTHENTICATION_JWT_TYPE


class EndpointClass:
    endpoint_model = apps.get_model('transversal', 'Endpoint')

    def __init__(self):
        self.token = None
        self.headers = None
        self.authenticate()

    def authenticate(self):
        """JWT AUTH"""
        jwt_login_endpoint = self.endpoint_model.objects.filter(
            authentication_type_jwt=ENDPOINT_MODEL_AUTHENTICATION_JWT_TYPE['TOKEN_LOGIN']).first()

        if jwt_login_endpoint:
            credentials = json.loads(jwt_login_endpoint.body)
            result = requests.post(jwt_login_endpoint.url, json=credentials)
            response = result.json()
            if not response['token']:
                raise Exception(_('Error to authenticate user'))

            self.token = response['token']
            self.headers = {'Authorization': f'{jwt_login_endpoint.authorization_header_prefix} {self.token}'}

    def refresh_token(self):
        jwt_refresh_endpoint = self.endpoint_model.objects.filter(
            authentication_type_jwt=ENDPOINT_MODEL_AUTHENTICATION_JWT_TYPE['TOKEN_REFRESH']).first()

        if jwt_refresh_endpoint:
            token = self.token
            result = requests.post(jwt_refresh_endpoint.url, json={'token': token})
            response = result.json()
            self.token = response['token']

    # HTTP FUNCTIONS
    def get(self, url, **kwargs):
        res = requests.get(url, headers=self.headers, **kwargs)
        return res.json()

    def post(self, url, **kwargs):
        res = requests.post(url, headers=self.headers, **kwargs)
        return res.json()

    def put(self, url, **kwargs):
        res = requests.put(url, headers=self.headers, **kwargs)
        return res.json()

    def patch(self, url, **kwargs):
        res = requests.patch(url, headers=self.headers, **kwargs)
        return res.json()

    def delete(self, url, **kwargs):
        res = requests.delete(url, headers=self.headers, **kwargs)
        return res.json()
