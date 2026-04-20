from django.urls import path

from two_factor.views import (
    ProfileView,
)
from two_factor_custom.views.core import LoginCustomView, qr_code

core = [
    path(
        'account/login/',
        LoginCustomView.as_view(),
        name='login',
    ),
]

profile = [
    path(
        'account/two_factor/',
        ProfileView.as_view(),
        name='profile',
    ),
    path(
        'account/two_factor/qr-code',
        qr_code,
        name='qr-code',
    ),
]

urlpatterns = (core + profile, 'two_factor')
