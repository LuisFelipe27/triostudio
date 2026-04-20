from datetime import datetime
from django.core.management import BaseCommand
from django.db import connection
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from multi_tenant.models import Cliente
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
    help = _("Asignación de permisos a todos los grupos")

    def assign_permission(self, schema_name, permission_name):
        os.system("")
        print(style.BLUE + "=== START ASSIGN PERMISSION === " + style.RESET)

        if schema_name:
            clients = Cliente.objects.filter(schema_name=schema_name).exclude(is_principal=False)
        else:
            clients = Cliente.objects.filter(
                Q(configcliente__expiracion__gt=datetime.today()) |
                Q(configcliente__expiracion__isnull=True)
            ).exclude(schema_name='public').exclude(is_principal=False)

        for client in clients:
            connection.schema_name = client.schema_name
            print(style.MAGENTA + "=== LOAD DATA '" + client.nombre + "' === " + style.RESET)

            permission = Permission.objects.get(
                codename=permission_name
            )

            groups = Group.objects.all()

            for group in groups:
                group.permissions.add(permission)
                print(f'{style.GREEN} ADDED PERMISSION {permission_name}  TO GROUP {group.name}{style.RESET}')

        print(style.BLUE + "=== END LOAD DATA === " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-sn', '--schema_name', type=str, help='Nombre schema del cliente a cargar data', )
        parser.add_argument('-pn', '--permission_name', type=str, help='Codename del permiso a asignar', )

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        permission_name = options['permission_name']

        self.assign_permission(schema_name, permission_name)

