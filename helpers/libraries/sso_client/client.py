from copy import copy
from urllib.parse import urlunparse, urljoin, urlencode
from django.http import HttpResponseRedirect
from django.apps import apps
from django.urls import NoReverseMatch, reverse
from django.contrib.auth import login
from django.contrib.auth.models import User
from simple_sso.sso_client.client import LoginView, Client
from helpers.functions.utils import get_parametro
from itsdangerous import URLSafeTimedSerializer
from webservices.sync import SyncConsumer


class LoginCustomView(LoginView):
    def get(self, request):
        next = self.get_next()
        scheme = 'https' if request.is_secure() else 'http'
        query = urlencode([('next', next)])
        netloc = request.get_host()
        path = reverse('simple-sso-authenticate')
        redirect_to = urlunparse((scheme, netloc, path, '', query, ''))
        request_token = self.client.get_request_token(redirect_to)
        host = urljoin(get_parametro('SSO_SERVER_URL'), 'authorize/')
        url = '%s?%s' % (host, urlencode([('token', request_token)]))
        return HttpResponseRedirect(url)


class AuthenticateCustomView(LoginCustomView):
    def get(self, request):
        raw_access_token = request.GET['access_token']
        access_token = URLSafeTimedSerializer(get_parametro('SSO_PRIVATE_KEY')).loads(raw_access_token)
        user = self.client.get_user(access_token)
        user.backend = self.client.backend
        login(request, user)
        next = self.get_next()
        return HttpResponseRedirect(next)


class ClientSSO(Client):
    login_view = LoginCustomView
    authenticate_view = AuthenticateCustomView

    def __init__(self, user_extra_data=None):
        if user_extra_data:
            self.user_extra_data = user_extra_data

    def get_request_token(self, redirect_to):
        try:
            url = reverse('simple-sso-request-token')
        except NoReverseMatch:
            # thisisfine
            url = '/request-token/'
        consumer = SyncConsumer(
            get_parametro('SSO_SERVER_URL'), get_parametro('SSO_PUBLIC_KEY'), get_parametro('SSO_PRIVATE_KEY')
        )
        return consumer.consume(url, {'redirect_to': redirect_to})['request_token']

    def get_user(self, access_token):
        data = {'access_token': access_token}
        if self.user_extra_data:
            data['extra_data'] = self.user_extra_data

        try:
            url = reverse('simple-sso-verify')
        except NoReverseMatch:
            # thisisfine
            url = '/verify/'

        consumer = SyncConsumer(
            get_parametro('SSO_SERVER_URL'), get_parametro('SSO_PUBLIC_KEY'), get_parametro('SSO_PRIVATE_KEY')
        )
        user_data = consumer.consume(url, data)
        user = self.build_user(user_data)
        return user

    def build_user(self, user_data):
        create_profile = False
        try:
            user = User.objects.get(username=user_data['username'])
            # Update user data, excluding username changes
            # Work on copied _tmp dict to keep an untouched user_data
            user_data_tmp = copy(user_data)
            del user_data_tmp['username']
            for _attr, _val in user_data_tmp.items():
                setattr(user, _attr, _val)
        except User.DoesNotExist:
            user = User(**user_data)
            create_profile = True

        user.set_unusable_password()
        user.save()
        if create_profile:
            profile = apps.get_model('transversal', 'Perfil')
            profile(usuario=user).save(set_password=False)
        return user
