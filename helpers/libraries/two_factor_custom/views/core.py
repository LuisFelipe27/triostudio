from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views import LoginView
from two_factor_custom.forms.login import AuthenticationCustomForm

from helpers.functions.utils import get_client_ip, get_parametro
from helpers.middleware.request_current import get_current_request


class LoginCustomView(LoginView):
    form_list = (
        ('auth', AuthenticationCustomForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )

    def bypass_by_ip(self):
        request = get_current_request()
        IP_CLIENT = get_client_ip(request)
        return bool(
            IP_CLIENT in str(get_parametro('TWO_FACTOR_IP_BYPASS')).split(',') or
            get_parametro('TWO_FACTOR_ENABLED') == '0'
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None
        self.cookies_to_delete = []
        self.show_timeout_error = False

        if self.bypass_by_ip():
            self.condition_dict = {
                'token': False,
                'backup': False,
            }

    # Copied from django.contrib.auth.views.LoginView  (Branch: stable/1.11.x)
    # https://github.com/django/django/blob/58df8aa40fe88f753ba79e091a52f236246260b3/django/contrib/auth/views.py#L49
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if get_parametro('ACTIVATE_SINGLE_SIGN_ON_IN_ORDENADITO') == '1':
            return HttpResponseRedirect('/client/')
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)


@login_required
def qr_code(request):
    try:
        import qrcode
        import qrcode.image.svg

        totpdevice = request.user.totpdevice_set.first()

        img = qrcode.make(totpdevice.config_url, image_factory=qrcode.image.svg.SvgImage)
        response = HttpResponse(content_type='image/svg+xml')
        img.save(response)

    except ImportError:
        response = HttpResponse('', status=503)

    return response
