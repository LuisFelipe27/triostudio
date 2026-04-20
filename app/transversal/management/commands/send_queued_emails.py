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
from helpers.functions.utils import elimina_tildes, removeNonAscii, get_parametro
from multi_tenant.models import Cliente
from transversal.models import NotificacionEmail
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
    help = _("Enviar los correos electrónicos en cola")

    def send_queued_emails(self, schema_name):
        os.system("")
        print(style.BLUE + "=== START LOAD DATA === " + style.RESET)

        if schema_name:
            clients = Cliente.objects.filter(schema_name=schema_name)
        else:
            clients = Cliente.objects.filter(
                Q(configcliente__expiracion__gt=datetime.today()) |
                Q(configcliente__expiracion__isnull=True)
            ).exclude(schema_name='public').exclude(is_principal=False)

        for client in clients:
            connection.schema_name = client.schema_name
            print(style.MAGENTA + "=== SEND EMAILS '" + client.nombre + "' === " + style.RESET)

            now = datetime.now()

            notifications = NotificacionEmail.objects.filter(
                es_enviada=False,
                created__year=now.year,
                created__month=now.month,
                created__day=now.day,
            )

            for notification in notifications:
                notification.save()

                print(style.GREEN + "SUCCESS: Notification ID:" + str(notification.id) + style.RESET)

        print(style.BLUE + "=== END SEND EMAILS === " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-sn', '--schema_name', type=str, help='Nombre schema del cliente a enviar correos en cola', )

    def handle(self, *args, **options):
        schema_name = options['schema_name']

        self.send_queued_emails(schema_name)

