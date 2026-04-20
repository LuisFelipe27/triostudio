from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = (
    ('es', 'Español'),
)

CLIENTS_LANGUAGE_CHOICES = ()

ENDPOINT_MODEL_TYPE = {
    'LOGIN': 1,
    'USERS': 2,
}

ENDPOINT_MODEL_AUTHENTICATION_TYPE = {
    'JWT': 1
}

ENDPOINT_MODEL_INTEGRATION_TYPE = {
    'REST': 1
}

ENDPOINT_MODEL_AUTHENTICATION_JWT_TYPE = {
    'TOKEN_LOGIN': 1,
    'TOKEN_REFRESH': 2,
    'TOKEN_VERIFY': 3
}


PARAMETERS_TYPES = ((1, _('Texto Libre')), (2, _('Selección')))

PARAMETER_TYPE = {
    'INPUT': 1,
    'SELECT': 2
}

TEMPLATE_DOCUMENTO_FIJO = {
    'LIQUIDATION': 1,
    'LIQUIDATION_ITEM': 2
}

TEMPLATE_NOTIFICATION = {
    'ACCESS_CREDENTIALS': 1,
    'AUTHENTICATION_TWO_FACTOR': 2,
}


RECAPTCHA_V3 = {
    'RECAPTCHA_SITE_KEY': '',
    'RECAPTCHA_SECRET_KEY': ''
}


MONTHS = ((1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'),
          (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'),
          (12, 'Diciembre'))


TWILIO_NOTIFICATION_TYPE = {
    'SMS': 1,
    'WHATSAPP': 2
}

SMS_RESPONSE_TYPE = {
    'NO': 0,
    'SI': 1
}

DOCUMENT_FORMAT = {
    "WORD": 1,
    "PDF": 2,
}


PROPERTY_STATUS_CHOICES = ((1, _('Disponible')), (2, _('Ocupado')))

DEFAULT_READONLY_FIELDS = ('created', 'created_by', 'modified', 'modified_by')


SYSTEM_PARAMETERS = [
    {
        'key': 'EMAIL_FOOTER',
        'value': 'https://i.postimg.cc/tgBqJxPf/logotipo-ordenadito-441x272.png',
        'parameter_type': 'input',
        'description': ''
    },
    {
        'key': 'EMAIL_HEADER',
        'value': 'https://i.postimg.cc/tgBqJxPf/logotipo-ordenadito-441x272.png',
        'parameter_type': 'input',
        'description': ''
    },
    {
        'key': 'SIEMPRE_MAYUSCULAS',
        'value': '0',
        'parameter_type': 'select',
        'description': _('Muestra en Mayusculas los campos de tipo input, search y textarea')
    },
    {
        'key': 'TWO_FACTOR_IP_BYPASS',
        'value': '',
        'parameter_type': 'input',
        'description': _('IP a dejar libre de uso de doble factor, para ingresar mas de 1 separarlas por ,')
    },
    {
        'key': 'TWO_FACTOR_ENABLED',
        'value': '0',
        'parameter_type': 'select',
        'description': _('Habilita o deshabilita el uso de doble factor')
    },
    {
        'key': 'ACTIVATE_SINGLE_SIGN_ON_IN_ORDENADITO',
        'value': '',
        'parameter_type': 'input',
        'description': _('Activar Single Sign on para clientes Ordenadito')
    },
    {
        'key': 'SSO_SERVER_URL',
        'value': '',
        'parameter_type': 'input',
        'description': _('URL Host Server Ordenadito SSO, Cliente Ordenadito que usa Single Sign On, '
                         'debe terminar en /server/, Ejemplo: https://xxx.ordenadito.cl/server/')
    },
    {
        'key': 'SSO_PUBLIC_KEY',
        'value': '',
        'parameter_type': 'input',
        'description': _('Clave Publica que Emite Host Server Ordenadito Single Sign On')
    },
    {
        'key': 'SSO_PRIVATE_KEY',
        'value': '',
        'parameter_type': 'input',
        'description': _('Clave Privada que Emite Host Server Ordenadito Single Sign On')
    },
]
