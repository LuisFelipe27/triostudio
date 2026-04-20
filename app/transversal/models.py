from __future__ import unicode_literals
from django.apps import apps
from django.contrib.auth.models import User, Group
from django.contrib.postgres.fields import ArrayField
from django.db import models, connection
from django.dispatch import receiver
from bunch import Bunch
from jinja2 import Template
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from helpers.constants import PARAMETER_TYPE, PARAMETERS_TYPES, LANGUAGE_CHOICES
from helpers.functions.utils import valid_run, tenant_current
from helpers.classes.storage import LocalMediaStorage
from helpers.classes.models import RecordsModel
from helpers.classes.console_print import ConsolePrint

from helpers.constants import (
    TEMPLATE_NOTIFICATION, ENDPOINT_MODEL_AUTHENTICATION_TYPE, ENDPOINT_MODEL_INTEGRATION_TYPE
)
import os
from app.multi_tenant.models import Tenant
import json


class Endpoint(RecordsModel):
    METHOD = ((1, 'GET'), (2, 'POST'))
    TYPE = (
        (1, 'Login'), (2, _('Maestro de Usuarios'))
    )

    AUTHENTICATION_TYPE = ((1, 'JWT'),)
    AUTHENTICATION_JWT_TYPE = ((1, 'Token Login'), (2, 'Token Refresh'), (3, 'Token Verify'))
    INTEGRATION_TYPE = ((1, 'Rest'),)

    type = models.IntegerField(
        verbose_name=_('Tipo'), choices=TYPE, null=True
    )
    integration_type = models.IntegerField(
        verbose_name=_('Tipo de Integración'), choices=INTEGRATION_TYPE,
        null=True, default=ENDPOINT_MODEL_INTEGRATION_TYPE['REST']
    )
    authentication_type = models.IntegerField(
        verbose_name=_('Tipo de Autenticación'), choices=AUTHENTICATION_TYPE,
        null=True, default=ENDPOINT_MODEL_AUTHENTICATION_TYPE['JWT']
    )
    authentication_type_jwt = models.IntegerField(
        verbose_name=_('Tipo de Endpoint JWT'), choices=AUTHENTICATION_JWT_TYPE,
        null=True, blank=True
    )
    authorization_header_prefix = models.CharField(
        verbose_name=_('Prefijo Header Authorization'), max_length=200, blank=True, default='',
        help_text=_('Ejemplo: Bearer, Basic, Digest o Alguno Propio')
    )
    name = models.CharField(verbose_name=_('Nombre'), max_length=100)
    description = models.CharField(verbose_name=_('Descripción'), max_length=200, blank=True)
    url = models.URLField(verbose_name='URL', null=True)
    method = models.IntegerField(verbose_name=_('Tipo de Método'), choices=METHOD, null=True)
    query_params = models.TextField(
        verbose_name=_('Parametros Query'), blank=True,
        help_text=_('Query params que van en la url del endpoint')
    )
    body = models.TextField(
        verbose_name=_('Datos del Cuerpo'), blank=True, help_text=_('Utilizado para envio de datos en método POST')
    )

    class Meta:
        verbose_name = _("Endpoint")
        verbose_name_plural = _("Configurador de Endpoints")

    def __str__(self):
        return f'{self.name}'


class Perfil(models.Model):
    usuario = models.OneToOneField('auth.User', models.CASCADE)
    usuario_auth = models.CharField(max_length=200, null=True, blank=True)
    usuario_push = models.CharField(max_length=200, null=True, blank=True)
    run = models.CharField('R.U.N.', max_length=13, null=True, blank=True, validators=[valid_run])
    codigo_verificacion = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(verbose_name=_('Idioma'), default='es-ES', choices=LANGUAGE_CHOICES, max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    reset_password = models.BooleanField(
        u'¿Resetear contraseña y enviar por email?',
        default=False,
        help_text=u'Si está marcado se reseteará la contraseña y la enviará al email del usuario.'
    )
    tour = models.BooleanField(u'¿Forzar Tour?', default=False)

    access_only_for_api = models.BooleanField(
        _('Acceso solo a APIS'),
        default=False,
        help_text=_('Solo tendra acceso a las APIS del sistema, NO podra iniciar sesión de manera normal')
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def get_fullname(self):
        return "%s %s" % (self.usuario.first_name, self.usuario.last_name)

    def save(self, set_password=True, *args, **kwargs):
        if connection.schema_name != 'public' and (not self.id or self.reset_password):
            if self.usuario.email and set_password:
                ### Send credentials ###
                try:
                    Notificacion_model = apps.get_model('transversal', 'Notificacion')
                    Template_model = apps.get_model('transversal', 'TemplateNotificacion')

                    tenant = tenant_current()
                    template = Template_model.objects.get(
                        motivo_notificacion=TEMPLATE_NOTIFICATION['ACCESS_CREDENTIALS']
                    )
                    context = dict()
                    context['username'] = self.usuario.username
                    context['first_name'] = self.usuario.first_name
                    context['last_name'] = self.usuario.last_name
                    context['email'] = self.usuario.email
                    context['password'] = 'CvAHU74sPm'  # ToDo: random
                    self.usuario.set_password(context['password'])  # Reset password
                    self.usuario.save()
                    Notificacion_model(
                        template=template,
                        asunto='Credenciales de Acceso {} | {}'.format(self.usuario.username, tenant.name),
                        contexto=json.dumps(context),
                        otros_destinos='{},'.format(self.usuario.email)
                    ).save()

                except Exception as e:
                    ConsolePrint().error("Error", str(e))
                    pass

                self.reset_password = False

            if not self.id:
                self.tour = True
                self.show_modal_firma = True

                user = self.usuario
                twofactordevice = user.twofactordevice_set.first()
                if not twofactordevice:
                    TwoFactorDevice_model = apps.get_model('auth', 'TwoFactorDevice')
                    TwoFactorDevice_model.objects.create(
                        user=user,
                        name='default',
                        confirmed=True,
                        method='email'
                    )

                totpdevice = user.totpdevice_set.first()
                if not totpdevice:
                    from django_otp.plugins.otp_totp.models import TOTPDevice
                    TOTPDevice.objects.create(
                        user=user,
                        name='default',
                        confirmed=True
                    )

        super(Perfil, self).save(*args, **kwargs)

    def __str__(self):
        return "%s (%s %s)" % (self.usuario, self.usuario.first_name, self.usuario.last_name)


class UserTour(models.Model):
    usuario = models.ForeignKey('auth.User', models.CASCADE)
    tour = models.ForeignKey('multi_tenant.Tour', models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tour de Usuario"
        verbose_name_plural = "Tours de Usuarios"

    def __str__(self):
        return 'User: %s | Tour: %s' % (self.usuario, self.tour)


class Parameter(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    parameter_type = models.IntegerField(
        _('Tipo'), default=PARAMETER_TYPE['INPUT'], choices=PARAMETERS_TYPES)
    parameter_choices = ArrayField(models.CharField(max_length=50), default=list)
    description = models.TextField(verbose_name=_('Descripción'), default='')

    class Meta:
        ordering = ['key']
        verbose_name = _("Parámetro")
        verbose_name_plural = _("Parámetros")

    def __str__(self):
        return f'{self.key}'


class NotificationMailProvider(models.Model):
    INTEGRATION = ( (1,'POP3'), (2,'SMTP'))

    name = models.CharField(max_length=200)
    is_active = models.BooleanField(_('¿Está activa?'), default=True)
    is_principal = models.BooleanField(_('¿Es principal?'), default=False)
    integration = models.IntegerField(_('Integración'), choices=INTEGRATION)

    def parameters(self):
        params = NotificationMailProviderParam.objects.filter(provider=self.id)
        parameters = Bunch()
        parameters.EMAIL_HOST = params.filter(key='EMAIL_HOST').last().value
        parameters.EMAIL_PORT  = params.filter(key='EMAIL_PORT').last().value
        parameters.EMAIL_HOST_USER = params.filter(key='EMAIL_HOST_USER').last().value
        parameters.EMAIL_HOST_PASSWORD = params.filter(key='EMAIL_HOST_PASSWORD').last().value
        parameters.DEFAULT_FROM_EMAIL = params.filter(key='DEFAULT_FROM_EMAIL').last().value
        parameters.SERVER_EMAIL = params.filter(key='SERVER_EMAIL').last().value
        parameters.EMAIL_SUBJECT_PREFIX = params.filter(key='EMAIL_SUBJECT_PREFIX').last().value
        try:
            parameters.EMAIL_USE_TLS = params.filter(key='EMAIL_USE_TLS').last().value
            parameters.EMAIL_USE_SSL = params.filter(key='EMAIL_USE_SSL').last().value
        except Exception:
            pass
        return parameters

    class Meta:
        verbose_name = _("Proveedor de Email")
        verbose_name_plural = _("Notificaciones | Proveedor de Email")

    def __str__(self):
        return self.name


class NotificationMailProviderParam(models.Model):
    KEYS = (
        #Mail
            ('EMAIL_HOST', 'EMAIL_HOST'),
            ('EMAIL_PORT', 'EMAIL_PORT'),
            ('EMAIL_HOST_USER','EMAIL_HOST_USER'),
            ('EMAIL_HOST_PASSWORD', 'EMAIL_HOST_PASSWORD'),
            ('DEFAULT_FROM_EMAIL', 'DEFAULT_FROM_EMAIL'),
            ('SERVER_EMAIL', 'SERVER_EMAIL'),
            ('EMAIL_SUBJECT_PREFIX', 'EMAIL_SUBJECT_PREFIX'),
            ('EMAIL_USE_TLS', 'EMAIL_USE_TLS'),
            ('EMAIL_USE_SSL', 'EMAIL_USE_SSL'),
        )

    provider = models.ForeignKey('transversal.NotificationMailProvider', models.CASCADE)
    key = models.CharField(max_length=250, choices=KEYS)
    value = models.CharField(max_length=250)

    class Meta:
        verbose_name = _("Parámetro Email")
        verbose_name_plural = _("Notificaciones | Parámetros Email")

    def __str__(self):
        return "%s %s" % (self.provider, self.key)


class TemplateNotification(models.Model):
    CHOICES_REASON = (
        (1, 'Creación de cuenta',),
        (2, 'Inscripción de Torneo',),
        (3, 'Resultado de Partido',),
        (4, 'Publicación de Cuadros',),
        (5, 'Informativos varios',),
    )

    name = models.CharField(max_length=250, null=True)
    reason = models.IntegerField(choices=CHOICES_REASON, verbose_name=_('Motivo'), null=True)
    mail_provider = models.ForeignKey('transversal.NotificationMailProvider', models.CASCADE,
                                      verbose_name=_('Email Provider'), null=True, blank=True)
    html = models.TextField(help_text=_('HTML El cuerpo del correo.'))

    class Meta:
        verbose_name = _("Plantilla de Notificación")
        verbose_name_plural = "Plantillas de Notificaciones"

    def __str__(self):
        return "%s" % self.name


class Notification(RecordsModel):
    template = models.ForeignKey('transversal.TemplateNotification', models.CASCADE)
    subject = models.CharField(max_length=200)
    context = models.TextField(blank=True)
    destination = models.TextField(blank=True, null=True, verbose_name=_("Destinatarios"))
    is_read  = models.BooleanField('¿Está leída?', default=False)

    @property
    def message(self):
        from django.template.loader import get_template, render_to_string
        try:
            json_context = json.loads(self.contexto)
        except Exception as e:
            json_context = {}
        template = Template( self.template.html )
        try:
            body_context = template.render(contexto = json_context)
        except:
            body_context = None
        return body_context

    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones | Notificaciones")

    def __str__(self):
        return self.subject


class NotificationEmail(RecordsModel):
    notification = models.ForeignKey('transversal.Notification', models.CASCADE, default=None, null=True, related_name="email_messages")
    is_send = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Notificación Email")
        verbose_name_plural = _("Notificaciones | Notificaciones Email")

    def __str__(self):
        return self.notification.subject


from binascii import unhexlify
from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
from django_otp.models import Device, ThrottlingMixin
from django.conf import settings

TWOFACTOR_METHODS = (
    ('email', _('Correo electrónico')),
    ('token', _('Google Authenticator')),
)


def key_validator(*args, **kwargs):
    """Wraps hex_validator generator, to keep makemigrations happy."""
    return hex_validator()(*args, **kwargs)


class TwoFactorDevice(ThrottlingMixin, Device):
    """
    Model with method and token seed linked to a user.
    """

    class Meta:
        app_label = 'auth'
        verbose_name = _("Cuenta Doble Factor")
        verbose_name_plural = _("Cuentas Doble Factor")

    key = models.CharField(max_length=40,
                           validators=[key_validator],
                           default=random_hex,
                           help_text="Hex-encoded secret key")
    method = models.CharField(max_length=5, choices=TWOFACTOR_METHODS,
                              default='email', verbose_name=_('Método'))

    def __repr__(self):
        return '<TwoFactorDevice(user={!r}, method={!r}>'.format(
            self.user.username,
            self.method,
        )

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def verify_token(self, token):
        # local import to avoid circular import
        from two_factor.utils import totp_digits

        try:
            token = int(token)
        except ValueError:
            return False

        for drift in range(-5, 1):
            if totp(self.bin_key, drift=drift, digits=totp_digits()) == token:
                return True
        return False

    def generate_challenge(self):
        # local import to avoid circular import
        from two_factor.utils import totp_digits

        """
        Sends the current TOTP token to `self.number` using `self.method`.
        """
        no_digits = totp_digits()
        token = str(totp(self.bin_key, digits=no_digits)).zfill(no_digits)
        if self.method == 'email':
            template = TemplateNotificacion.objects.get(
                motivo_notificacion=TEMPLATE_NOTIFICATION['AUTHENTICATION_TWO_FACTOR']
            )
            context = dict()
            context['user'] = {
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
            }
            context['token'] = token
            tenant = tenant_current()

            Notificacion.objects.create(
                template=template,
                asunto='Autenticación de Doble Factor para {}'.format(tenant.domain_url),
                contexto=json.dumps(context),
                otros_destinos=self.user.email
            )

    def get_throttle_factor(self):
        return getattr(settings, 'TWO_FACTOR_PHONE_THROTTLE_FACTOR', 1)


class Permisos(models.Model):
    """ Esto es sólamente para controlar los permisos de la aplicación transversal.
	"""

    class Meta:
        default_permissions = ()
        permissions = (
            ('can_access_transversal', 'Puede acceder al módulo de Transversal'),
        )
