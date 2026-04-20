from config.config import *
import os
import sys
import logging.config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.join(BASE_DIR, 'helpers/libraries'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9%p=jtp7@wd0vam(7epz3gpn_5dytnq&_xtgh9yb!b(#0sty_&'
FIELD_ENCRYPTION_KEY = ENVIRONMENT.get(
    'crypto_key', 'TPzBGQ_6-RpD4Gn9dKeCaS2r7bhI2J7O9P2rdNcXyBs=')

ALLOWED_HOSTS = ['.triostudio.cl']

# The age of session cookies, in seconds. Default: 1209600 (2 weeks, in seconds)
SESSION_COOKIE_AGE = 1209600  # 2 weeks

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB; default 2.5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # default 1000
FILE_UPLOAD_PERMISSIONS = 0o644  # force 644 file permissions

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SHARED_APPS = (
    'tenant_schemas',  # mandatory
    'app.multi_tenant',
    'app.django_admin_inline_paginator',
    'admin_auto_filters',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'rest_framework_datatables',
    'corsheaders',
    'colorfield',
    'import_export',
    'prettyjson',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'auditlog',
    'two_factor',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',

    'app.audit_module',
)

TENANT_APPS = (
    # The following Django contrib apps must be in TENANT_APPS
    'admin_auto_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_extensions',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'auditlog',
    'two_factor',

    'app.django_admin_inline_paginator',
    'app.audit_module',
    'app.transversal',
    'app.halftone',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
)

TENANT_MODEL = "multi_tenant.Tenant"  # app.Model

# Application definition
INSTALLED_APPS = [
    'tenant_schemas',
    'app.multi_tenant',
    'app.django_admin_inline_paginator',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.postgres',
    'django_extensions',
    'django_filters',
    'rest_framework',
    'corsheaders',
    'colorfield',
    'import_export',
    'storages',
    'prettyjson',
    'django.forms',
    'rest_framework_jwt',
    'rest_framework_datatables',
    'channels',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'auditlog',
    'two_factor',

    'app.audit_module',
    'app.transversal',
    'app.halftone',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'admin_auto_filters',
]

MIDDLEWARE = [
    'tenant_schemas.middleware.TenantMiddleware',
    'helpers.middleware.request_current.RequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

if USE_REQUEST_LOG:
    MIDDLEWARE.append('helpers.middleware.request_log.RequestLogMiddleware')

if USE_SYSTEM_LOG:
    MIDDLEWARE.append('auditlog.middleware.AuditlogMiddleware')

    AUDITLOG_INCLUDE_ALL_MODELS = True
    AUDITLOG_EXCLUDE_TRACKING_MODELS = (
        'audit_module',
        'django.contrib.sessions.Session',
    )

ROOT_URLCONF = 'config.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'config.urls_public'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'app', 'transversal', 'templates'),
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',

                'helpers.context_processors.parameters.parameters',
                'helpers.context_processors.captcha.recaptcha_site_key',
                'helpers.context_processors.constants.constants_config',
                'helpers.context_processors.constants.constants_transversal'
            ],
            'builtins': [
                'django.templatetags.static',
                'django.templatetags.i18n',
            ]
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_ROUTERS = (
    'tenant_schemas.routers.TenantSyncRouter',
)

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = DEFAULT_LANGUAGE_CODE
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = (
    ('en', 'English'),
    ('es', 'Spanish'),
)

if USE_S3:
    # aws settings
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # AWS_QUERYSTRING_EXPIRE = '900'  # 5 minutes; default 3600 (1 hour)
    # s3 static settings
    # STATIC_LOCATION = 'static'
    # STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    # STATICFILES_STORAGE = 'helpers.classes.storage.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    MEDIA_URL_SELF = '/media/'
    DEFAULT_FILE_STORAGE = 'helpers.classes.storage.PrivateMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'media'
    PRIVATE_FILE_STORAGE = 'helpers.classes.storage.PrivateMediaStorage'
else:
    DEFAULT_FILE_STORAGE = 'helpers.classes.storage.LocalMediaStorage'

    MEDIA_URL = '/media/'
    MEDIA_URL_SELF = MEDIA_URL

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework_datatables.filters.DatatablesFilterBackend'
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'helpers.middleware.rest_framwork_fix.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}

ASGI_APPLICATION = 'config.routing.application'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Keli API',
    'CONTACT': {'name': 'Soporte', 'email': 'soporte@ordenadito.cl'},
    'VERSION': '0.0.1',
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
    'REDOC_UI_SETTINGS': {
       'downloadDefinitionUrl': '/api/schema/?format=json',
    }
}

CORS_ORIGIN_ALLOW_ALL = True

# LOGIN_URL = '/accounts/login/'
# LOGOUT_REDIRECT_URL = '/accounts/login/'

LOGOUT_REDIRECT_URL = 'two_factor:login'
LOGIN_URL = 'two_factor:login'
# this one is optional
LOGIN_REDIRECT_URL = '/'

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale'), ]

if ENVIRONMENT['name'] == 'local':
    from config.settings_env.local import *

if ENVIRONMENT['name'] == 'dev':
    from config.settings_env.dev import *

if ENVIRONMENT['name'] == 'qa':
    from config.settings_env.qa import *

if ENVIRONMENT['name'] == 'rc':
    from config.settings_env.rc import *

if ENVIRONMENT['name'] == '':
    from config.settings_env.production import *


# ---------------------------------------------------------------------------
# Celery / Redis (TrioStudio - halftone async pipeline)
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 4 * 60
# When the broker is unreachable (e.g. local dev without redis) the views
# fall back to inline execution; this prevents long retries.
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = False
CELERY_BROKER_TRANSPORT_OPTIONS = {'max_retries': 1}