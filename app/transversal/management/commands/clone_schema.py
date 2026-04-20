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
from helpers.functions.utils import (
    elimina_tildes,
    removeNonAscii,
    get_parametro,
    format_date,
    printProgressBar
)
import json
import os
import sys
import time


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
    help = _("Clone Schema")

    def clone_schema(self, source_schema, target_schema, copy_data=True, clear_data_sensible=True):
        os.system("")
        print(style.BLUE + "=== START CLONE SCHEMA === " + style.RESET)

        printProgressBar(10, 100, prefix='Cloning schema:', suffix='Complete', length=50)
        cursor = connection.cursor()
        cursor.execute(f"SELECT public.copy_schema('{source_schema}', '{target_schema}', {copy_data})")
        printProgressBar(40, 100, prefix='Cloning schema:', suffix='Complete', length=50)

        if copy_data and clear_data_sensible:
            connection.schema_name = target_schema
            User_model = apps.get_model('auth', 'User')
            Professional_model = apps.get_model('agenda', 'Profesional')
            Patient_model = apps.get_model('pacientes', 'Paciente')

            printProgressBar(60, 100, prefix='Deleting patients:', suffix='Complete', length=50)
            Patient_model.objects.all().delete()

            printProgressBar(80, 100, prefix='Deleting professionals:', suffix='Complete', length=50)
            Professional_model.objects.all().delete()

            printProgressBar(90, 100, prefix='Deleting users:', suffix='Complete', length=50)
            User_model.objects.exclude(email__icontains='ordenadito.cl').exclude(username='admin').delete()

        printProgressBar(100, 100, prefix='Cloning schema:', suffix='Complete', length=50)

        print(style.BLUE + "=== END CLONE SCHEMA === " + style.RESET)

    def add_arguments(self, parser):
        parser.add_argument('-ss', '--source_schema', type=str, help='Schema name to copy', )
        parser.add_argument('-ts', '--target_schema', type=str, help='Schema name new', )
        parser.add_argument('-cd', '--copy_data', type=bool, help=_('Copy schema with data'))
        parser.add_argument('-cds', '--clear_data_sensible', type=bool, help=_('Deleting data sensible'))

    def handle(self, *usernames, **options):
        source_schema = options['source_schema']
        target_schema = options['target_schema']
        copy_data = bool(options['copy_data'])
        clear_data_sensible = bool(options['clear_data_sensible'])

        if not source_schema or not target_schema:
            print(style.RED + "ERROR: missing params required " + style.RESET)
        else:
            self.clone_schema(source_schema, target_schema, copy_data, clear_data_sensible)
