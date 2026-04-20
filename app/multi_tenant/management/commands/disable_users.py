from datetime import datetime
from django.apps import apps
from django.db import connection
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
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
    """
    Command for disable all or certain users.
    The command accepts any number of usernames, and optional one schema name.
    Example usage:
        manage.py disable_users --schema_name=schemaxxxxxxxxxxx bouke steve
    """
    help = _("Deshabilitar usuarios de todos o algunos clientes")

    def disable_users(self, schema_name, usernames):
        os.system("")
        now = datetime.now()
        print(style.BLUE + "=== START DISABLE USERS === " + style.RESET)

        Client_model = apps.get_model('multi_tenant', 'Cliente')
        User_model = apps.get_model('auth', 'User')

        if schema_name:
            clients = Client_model.objects.filter(schema_name=schema_name).exclude(is_principal=False)
        else:
            clients = Client_model.objects.filter(
                Q(configcliente__expiracion__gt=datetime.today()) |
                Q(configcliente__expiracion__isnull=True)
            ).exclude(schema_name='public').exclude(is_principal=False)

        for client in clients:
            connection.schema_name = client.schema_name
            print(style.MAGENTA + "=== DISABLE USERS '" + client.nombre + "' === " + style.RESET)

            if not usernames:
                usernames = User_model.objects.values_list('username', flat=True)

            for username in usernames:
                try:
                    user = User_model.objects.get_by_natural_key(username)
                    user.is_active = False
                    user.save()
                    print(style.GREEN + "User '"+str(username)+"' DISABLED" + style.RESET)

                except User_model.DoesNotExist:
                    print(style.RED + "User '"+str(username)+"' does not exist" + style.RESET)

        print(style.BLUE + "=== END DISABLE USERS === " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-sn', '--schema_name', type=str, help='Nombre schema del cliente a cargar data', )
        parser.add_argument('args', metavar='usernames', nargs='*')

    def handle(self, *usernames, **options):
        schema_name = options['schema_name']

        self.disable_users(schema_name, usernames)

