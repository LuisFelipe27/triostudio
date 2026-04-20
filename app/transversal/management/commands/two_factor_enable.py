from datetime import datetime, timedelta
from django.apps import apps
from django.db import connection
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User, Permission
from django.utils.translation import gettext_lazy as _
from config.settings import MEDIA_ROOT
from helpers.functions.export_document import (
    export_documento, remove_file_temp, remove_directory_temp,
    copy_file_temp, zip_file_temp)
from helpers.functions.utils import elimina_tildes, removeNonAscii, get_parametro, format_date
import json
import os
import sys


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
    Command for enable two-factor authentication for all or certain users.

    The command accepts any number of usernames, and will enable all OTP
    devices for those users, as too the two-factor by email.

    Example usage:

        manage.py two_factor_enable --schema_name=schemaxxxxxxxxxxx bouke steve
    """
    help = _("Habilitación de Autenticación de Doble Factor")

    def two_factor_enable(self, schema_name, usernames):
        os.system("")
        print(style.BLUE + "=== START ENABLE TWO-FACTOR === " + style.RESET)

        Client_model = apps.get_model('multi_tenant', 'Cliente')
        User_model = apps.get_model('auth', 'User')
        TwoFactorDevice_model = apps.get_model('auth', 'TwoFactorDevice')
        from django_otp.plugins.otp_totp.models import TOTPDevice

        if schema_name:
            clients = Client_model.objects.filter(schema_name=schema_name).exclude(is_principal=False)
        else:
            clients = Client_model.objects.filter(
                Q(configcliente__expiracion__gt=datetime.today()) |
                Q(configcliente__expiracion__isnull=True)
            ).exclude(schema_name='public').exclude(is_principal=False)

        for client in clients:
            connection.schema_name = client.schema_name
            print(style.MAGENTA + "=== ENABLE USERS OF '" + client.nombre + "' === " + style.RESET)

            if not usernames:
                usernames = User_model.objects.values_list('username', flat=True)

            for username in usernames:
                try:
                    user = User_model.objects.get_by_natural_key(username)
                    twofactordevice = user.twofactordevice_set.first()
                    if not twofactordevice:
                        TwoFactorDevice_model.objects.create(
                            user=user,
                            name='default',
                            confirmed=True,
                            method='email'
                        )
                        print(style.GREEN + "User '"+str(username)+"' EMAIL CREATED" + style.RESET)

                    totpdevice = user.totpdevice_set.first()
                    if totpdevice:
                        totpdevice.confirmed = True
                        totpdevice.save()
                        print(style.GREEN + "User '"+str(username)+"' TOKEN UPDATED" + style.RESET)

                    else:
                        TOTPDevice.objects.create(
                            user=user,
                            name='default',
                            confirmed=True
                        )
                        print(style.GREEN + "User '"+str(username)+"' TOKEN CREATED" + style.RESET)

                except User.DoesNotExist:
                    print(style.RED + "User '"+str(username)+"' does not exist" + style.RESET)

        print(style.BLUE + "=== END ENABLE USERS === " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-sn', '--schema_name', type=str, help='Nombre schema del cliente', )
        parser.add_argument('args', metavar='usernames', nargs='*')

    def handle(self, *usernames, **options):
        schema_name = options['schema_name']

        self.two_factor_enable(schema_name, usernames)
