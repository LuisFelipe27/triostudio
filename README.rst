TrioStudio
=====================

|Django version| |Python version| |PostgreSQL|

TrioStudio: Diseño sin límites, detalle sin esfuerzo.

TrioStudio es una plataforma de procesamiento inteligente diseñada para optimizar la producción textil. Comenzando con un motor avanzado de conversión a semitonos, permite a los impresores de DTF transformar degradados complejos en tramas precisas, garantizando flexibilidad en la prenda, ahorro de tinta y una fidelidad de color excepcional. Es el puente técnico entre la creatividad y la realidad impresa, ofreciendo a los usuarios una herramienta poderosa para llevar sus diseños al siguiente nivel.


Deploy with Docker
---------------------

Es necesario crear un archivo ``.env`` en raíz del proyecto, el cual debe contener lo siguiente:

::

    COMPOSE_PROJECT_NAME=triostudio_local
    ENV_NAME=local
    IP_ADDRESS=172.18.1.10
    PORT_EXPOSE=8110
    PORT=81
    COUNTRY=CL


También debes crear un archivo ``config/gunicorn/conf.py``, el cual debe contener lo siguiente:

::

    name = 'triostudio'
    loglevel = 'info'
    errorlog = '-'
    accesslog = '-'
    workers = 2
    timeout = 300

    # Reinicio forzado de workers para liberar RAM
    # Un worker se reiniciará automáticamente tras procesar 1000 peticiones.
    max_requests = 1000

    # Escalonamiento de reinicios (Jitter)
    # Añade una variación aleatoria (0-50) al límite anterior para que
    # los 12 workers no reinicien todos al mismo tiempo.
    max_requests_jitter = 50

    # Carga eficiente en memoria (Copy-on-Write)
    # Carga la app una sola vez en el proceso maestro antes de crear los workers.
    # Esto reduce el consumo inicial y mejora el rendimiento.
    preload_app = True


Configuración del ambiente
---------------------

Necesitas crear el archivo ``config.py`` en el directorio ``config/`` del proyecto, y debe contener lo siguiente:

.. code-block:: python

    ENVIRONMENT = {
        'name': 'local', # local, dev, qa, rc --'production' is empty
        'IP': '127.0.0.1'
    }

    ADMINS = (
        ('NAME_ADMIN', 'EMAIL_ADMIN'),
    )

    MANAGERS = (
        ('NAME_MANAGER', 'EMAIL_MANAGER'),
    )

    DB_NAME = 'triostudio'
    DB_USER = '********'
    DB_PASSWORD = '************'
    # IF DEPLOY WITH DOCKER DB_HOST SHOULD BE YOUR LOCAL IP
    DB_HOST = '127.0.0.1'
    DB_PORT = '5432'

    USE_S3 = False
    # Configurar si corresponde al ambiente
    AWS_ACCESS_KEY_ID = '****************'
    AWS_SECRET_ACCESS_KEY = '**********************'
    AWS_STORAGE_BUCKET_NAME = 's3-ordenadito'

    DEFAULT_LANGUAGE_CODE = 'es'
    TIME_ZONE = 'America/Santiago'

    # CONFIG EMAIL
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 25
    EMAIL_HOST_USER = 'notifications@triostudio.cl'
    EMAIL_HOST_PASSWORD = '*****************'
    EMAIL_USE_TLS = True

    DEFAULT_FROM_EMAIL = 'TrioStudio Local <notifications@triostudio.cl>'
    SERVER_EMAIL = 'Django TrioStudio Local <notifications@triostudio.cl>'
    EMAIL_SUBJECT_PREFIX = '[App TrioStudio Local] '

    # PATH TO LIBREOFFICE FOR EXPORT DOCS TO PDF IN S.O WINDOWS (ONLY ADD IF NOT DEPLOY WITH DOCKER)
    LIBREOFFICE_WINDOWS_URL = '"C:/Program Files/LibreOffice/program/swriter.exe"'

    USE_REQUEST_LOG = True
    USE_SYSTEM_LOG = True
    COUNTRY_CODE = 'CL'

    # CREATE DNS CLOUDFLARE SETTINGS
    CLOUDFLARE_TOKEN = ''
    CLOUDFLARE_SERVER_IP = ''
    CLOUDFLARE_ZONE_IDENTIFIER = ''
    CLOUDFLARE_API_URL = 'https://api.cloudflare.com/client/v4'


Creación de Tenant inicial
---------------------

Despliegue proyecto  ``docker-compose up --build -d``


Creación de Tenant inicial
---------------------

Entra al contendor de la app ``docker exec -it [CONTAINER_NAME] bash`` y ejecuta lo siguiente:

.. code-block:: shell

    python manage.py makemigrations
    python manage.py migrate_schemas
    python manage.py collectstatic --no-input


Entra a la shell de django ``$ python manage.py shell`` y ejecuta lo siguiente:

.. code-block:: python

    from app.multi_tenant.models import Tenant

    Tenant(domain_url='tenant-local.triostudio.cl', schema_name='public', name='Triostudio').save()


Entra al contendor de la app ``docker exec -it [CONTAINER_NAME] bash`` y ejecuta lo siguiente:

.. code-block:: shell

    python manage.py createsuperuser


Manejo de parámetros del sistema
---------------------
Todos los parámetros deben estar en la constante ``SYSTEM_PARAMETERS`` en el archivo ``helpers/constants.py`` para que el django command ``python manage.py update_parameters`` de actualización de parámetros los considere.

Al django command se le puede configurar un parametro denomimado ``force_update=1``, el cual fuerza la actualizacion para los parametros existentes sin modificar el campo valor.

El campo ``parameter_type`` puede ser de tipo ``input`` o ``select``, si es de ``tipo select`` y las ``opciones validas`` son ``distintas de 1 o 0``, se debe ``incluir`` el campo ``choices``

Cada vez que se cree un nuevo parámetro, este debe ser incluido de la siguiente manera:

.. code-block:: python

    SYSTEM_PARAMETERS = [
        {
            'key': 'NEW_PARAMETER',
            'value': 'DEFAULT_VALUE',
            'parameter_type': 'input/select',
            'choices': ['OPTION_1', 'OPTION_2'],
            'description': 'DESCRIPTION FUNCTIONALITY OF THIS PARAMETER'
        },
        ...
    ]


Nota: para que el nuevo parámetro nuevo esté disponible en todos los esquemas (clientes) es necesario ejecutar el django command mencionado anteriormente.

Creación de Fixtures
---------------------

Entra a la shell de django al schema que se desee crear el fixture
``$ python manage.py tenant_command -s="nombre_schema" shell`` y ejecuta lo siguiente:

.. code-block:: python

    from django.core.management import call_command
    # Example: call_command('dumpdata', 'transversal.endpoint', indent=4, output='app/transversal/fixtures/endpoint.json')
    call_command('dumpdata', 'app_name.model_name', indent=4, output='path/to/save/file')


Carga de Fixtures
---------------------

Entra a la shell de django al schema que se desee cargar el fixture
``$ python manage.py tenant_command -s="nombre_schema" shell`` y ejecuta lo siguiente:

.. code-block:: python

    from django.core.management import call_command
    call_command('loaddata', 'fixture_name.json')


Icons Duotune Metronic
---------------------

Los iconos utilizados en el proyectos están disponibles en: ``https://preview.keenthemes.com/html/metronic/docs/icons/duotune#icons-listing``

.. code-block:: django

    {% getSvgIcon 'duotune/communication/com014.svg' 'svg-icon svg-icon-2x' %}


Template Theme Metronic
---------------------
Instalar la app ``theme`` y luego configurar lo siguiente en ``config/settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'app.theme',
        ...
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    ...
                ],
                'libraries': {
                    'theme': 'app.theme.templatetags.theme',
                },
                'builtins': [
                    'django.templatetags.static',
                    'app.theme.templatetags.theme',
                ]
            },
        },
    ]
    
    ######################
    # Keenthemes Settings
    ######################

    KT_THEME = 'metronic'


    # Theme layout templates directory

    KT_THEME_LAYOUT_DIR = 'layout'


    # Theme Mode
    # Value: light | dark | system

    KT_THEME_MODE_DEFAULT = 'light'
    KT_THEME_MODE_SWITCH_ENABLED = True

    # Sidebar Layout
    # Value: light | dark
    KT_THEME_SIDEBAR_LAYOUT = 'light'

    # Theme Direction
    # Value: ltr | rtl

    KT_THEME_DIRECTION = 'ltr'


    # Theme Assets

    KT_THEME_ASSETS = {
        "favicon": "media/logos/favicon.ico",
        "fonts": [
            'https://fonts.googleapis.com/css?family=Inter:300,400,500,600,700',
        ],
        "css": [
            "plugins/global/plugins.bundle.css",
            "css/style.bundle.css"
        ],
        "js": [
            "plugins/global/plugins.bundle.js",
            "js/scripts.bundle.js",
        ]
    }


    # Theme Vendors

    KT_THEME_VENDORS = {
        "datatables": {
            "css": [
                "plugins/custom/datatables/datatables.bundle.css"
            ],
            "js": [
                "plugins/custom/datatables/datatables.bundle.js"
            ]
        },
        "formrepeater": {
            "js": [
                "plugins/custom/formrepeater/formrepeater.bundle.js"
            ]
        },
        "fullcalendar": {
            "css": [
                "plugins/custom/fullcalendar/fullcalendar.bundle.css"
            ],
            "js": [
                "plugins/custom/fullcalendar/fullcalendar.bundle.js"
            ]
        },
        "flotcharts": {
            "js": [
                "plugins/custom/flotcharts/flotcharts.bundle.js"
            ]
        },
        "google-jsapi": {
            "js": [
                "//www.google.com/jsapi"
            ]
        },
        "tinymce": {
            "js": [
                "plugins/custom/tinymce/tinymce.bundle.js"
            ]
        },
        "ckeditor-classic": {
            "js": [
                "plugins/custom/ckeditor/ckeditor-classic.bundle.js"
            ]
        },
        "ckeditor-inline": {
            "js": [
                "plugins/custom/ckeditor/ckeditor-inline.bundle.js"
            ]
        },
        "ckeditor-balloon": {
            "js": [
                "plugins/custom/ckeditor/ckeditor-balloon.bundle.js"
            ]
        },
        "ckeditor-balloon-block": {
            "js": [
                "plugins/custom/ckeditor/ckeditor-balloon-block.bundle.js"
            ]
        },
        "ckeditor-document": {
            "js": [
                "plugins/custom/ckeditor/ckeditor-document.bundle.js"
            ]
        },
        "draggable": {
            "js": [
                "plugins/custom/draggable/draggable.bundle.js"
            ]
        },
        "fslightbox": {
            "js": [
                "plugins/custom/fslightbox/fslightbox.bundle.js"
            ]
        },
        "jkanban": {
            "css": [
                "plugins/custom/jkanban/jkanban.bundle.css"
            ],
            "js": [
                "plugins/custom/jkanban/jkanban.bundle.js"
            ]
        },
        "typedjs": {
            "js": [
                "plugins/custom/typedjs/typedjs.bundle.js"
            ]
        },
        "cookiealert": {
            "css": [
                "plugins/custom/cookiealert/cookiealert.bundle.css"
            ],
            "js": [
                "plugins/custom/cookiealert/cookiealert.bundle.js"
            ]
        },
        "cropper": {
            "css": [
                "plugins/custom/cropper/cropper.bundle.css"
            ],
            "js": [
                "plugins/custom/cropper/cropper.bundle.js"
            ]
        },
        "vis-timeline": {
            "css": [
                "plugins/custom/vis-timeline/vis-timeline.bundle.css"
            ],
            "js": [
                "plugins/custom/vis-timeline/vis-timeline.bundle.js"
            ]
        },
        "jstree": {
            "css": [
                "plugins/custom/jstree/jstree.bundle.css"
            ],
            "js": [
                "plugins/custom/jstree/jstree.bundle.js"
            ]
        },
        "prismjs": {
            "css": [
                "plugins/custom/prismjs/prismjs.bundle.css"
            ],
            "js": [
                "plugins/custom/prismjs/prismjs.bundle.js"
            ]
        },
        "leaflet": {
            "css": [
                "plugins/custom/leaflet/leaflet.bundle.css"
            ],
            "js": [
                "plugins/custom/leaflet/leaflet.bundle.js"
            ]
        },
        "amcharts": {
            "js": [
                "https://cdn.amcharts.com/lib/5/index.js",
                "https://cdn.amcharts.com/lib/5/xy.js",
                "https://cdn.amcharts.com/lib/5/percent.js",
                "https://cdn.amcharts.com/lib/5/radar.js",
                "https://cdn.amcharts.com/lib/5/themes/Animated.js"
            ]
        },
        "amcharts-maps": {
            "js": [
                "https://cdn.amcharts.com/lib/5/index.js",
                "https://cdn.amcharts.com/lib/5/map.js",
                "https://cdn.amcharts.com/lib/5/geodata/worldLow.js",
                "https://cdn.amcharts.com/lib/5/geodata/continentsLow.js",
                "https://cdn.amcharts.com/lib/5/geodata/usaLow.js",
                "https://cdn.amcharts.com/lib/5/geodata/worldTimeZonesLow.js",
                "https://cdn.amcharts.com/lib/5/geodata/worldTimeZoneAreasLow.js",
                "https://cdn.amcharts.com/lib/5/themes/Animated.js"
            ]
        },
        "amcharts-stock": {
            "js": [
                "https://cdn.amcharts.com/lib/5/index.js",
                "https://cdn.amcharts.com/lib/5/xy.js",
                "https://cdn.amcharts.com/lib/5/themes/Animated.js"
            ]
        },
        "bootstrap-select": {
            "css": [
                "plugins/custom/bootstrap-select/bootstrap-select.bundle.css"
            ],
            "js": [
                "plugins/custom/bootstrap-select/bootstrap-select.bundle.js"
            ]
        }
    }

Agregar en ``config/urls_public.py`` y en ``config/urls_tenants.py`` lo siguiente:

.. code-block:: python

    urlpatterns = [
        url(r'^theme/', include('app.theme.urls')),
    ]


.. _FactorDevops: https://factordevops.cl/

.. |Django version| image:: https://img.shields.io/badge/Django-v.3.2.7-brightgreen.svg
   :target: https://www.djangoproject.com/
.. |Python version| image:: https://img.shields.io/badge/Python-v3.7.4-yellow.svg
   :target: https://www.python.org/
.. |PostgreSQL| image:: https://img.shields.io/badge/PostgreSQL-v15.7-blue.svg
   :target: https://www.postgresql.org/
