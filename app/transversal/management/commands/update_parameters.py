from datetime import datetime
from django.apps import apps
from django.db import connection
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from helpers.constants import SYSTEM_PARAMETERS, PARAMETER_TYPE
import os


class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


class Command(BaseCommand):
    help = _("Actualización de parámetros del sistema")

    def update_parameters(self, schema_name, force_update):
        os.system("")
        print(style.BLUE + "=== START UPDATE OF PARAMETERS=== " + style.RESET)

        parameter_model = apps.get_model('transversal', 'Parameter')
        tenant_model = apps.get_model('multi_tenant', 'Tenant')
        if schema_name:
            clients = tenant_model.objects.filter(schema_name=schema_name)
        else:
            clients = tenant_model.objects.filter(
                Q(configtenant__expiracion__gt=datetime.today()) |
                Q(configtenant__expiracion__isnull=True)
            ).exclude(schema_name='public').exclude(is_principal=False)

        for client in clients:
            connection.schema_name = client.schema_name
            print(style.MAGENTA + "=== CLIENT '" + client.name + "' === " + style.RESET)

            for parameter_dict in SYSTEM_PARAMETERS:
                parameter_object = parameter_model.objects.filter(key=parameter_dict['key'])
                description = str(parameter_dict['description'])
                parameter_choices = list()
                if 'choices' in parameter_dict:
                    parameter_choices = parameter_dict['choices']

                if parameter_dict['parameter_type'] == 'input':
                    parameter_type = PARAMETER_TYPE['INPUT']
                else:
                    parameter_type = PARAMETER_TYPE['SELECT']

                if not parameter_object.exists():
                    parameter_model.objects.create(
                        key=parameter_dict['key'],
                        value=parameter_dict['value'],
                        parameter_type=parameter_type,
                        description=str(description),
                        parameter_choices=parameter_choices

                    )
                    print(style.GREEN + "SUCCESS Parameter created: " + parameter_dict['key'] + style.RESET)
                else:
                    if force_update:
                        parameter = parameter_object.first()
                        parameter.parameter_type = parameter_type
                        parameter.description = str(description)
                        parameter.parameter_choices = parameter_choices
                        parameter.save()
                        print(style.GREEN + "SUCCESS Parameter type updated: " + parameter_dict['key'] + style.RESET)

        print(style.BLUE + "=== END UPDATE OF PARAMETERS=== " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-sn', '--schema_name', type=str, help=_('Nombre schema del cliente'), )
        parser.add_argument('-fu', '--force_update', type=str, help=_('Flag(Si=1,No=0) para forzar actualizacion de campos tipo y choices'),)

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        force_update = False
        try:
            if 'force_update' in options and options['force_update'] and int(options['force_update']) == 1:
                force_update = True
        except:
            pass

        self.update_parameters(schema_name, force_update)
