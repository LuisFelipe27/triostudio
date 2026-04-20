from datetime import datetime
from django.db import connection
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from multi_tenant.models import Cliente
from app.audit_module.models import DatabaseBackupLog
import os
import csv


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
    help = _("Cargar log de datos de respaldos de esquemas base de datos")

    def load_data_log_backup_database(self):
        os.system("")
        print(style.BLUE + "=== START LOAD DATA === " + style.RESET)
        name_file = 'log_backup_database.txt'
        if os.path.exists(name_file):
            with open(name_file, encoding="utf-8", errors="ignore") as file:
                reader = csv.reader(file, delimiter=';')
                line_count = 0
                for row in reader:
                    # HEADER COLUMN
                    try:
                        if line_count == 0:
                            line_count += 1
                        elif row[2]:
                            schema_row = row[1]
                            event_date = datetime.strptime(row[0], '%d-%m-%Y %H:%M:%S')
                            description = row[2]

                            if schema_row:
                                client = Cliente.objects.filter(schema_name=schema_row).first()
                                if client:
                                    connection.schema_name = client.schema_name

                                    if not bool(DatabaseBackupLog.objects.filter(event_date=event_date,
                                            description=description)):
                                        DatabaseBackupLog.objects.create(
                                            event_date=event_date,
                                            description=description
                                        )
                                        print(style.GREEN + "SUCCESS: Log Schema " + str(client.nombre) + style.RESET)
                                    line_count += 1
                                else:
                                    line_count += 1
                            else:
                                line_count += 1
                        else:
                            line_count += 1
                    except Exception as e:
                        line_count += 1
                        pass

        else:
            print(style.RED + "ERROR: FILE NOT FOUND" + style.RESET)

        print(style.BLUE + "=== END LOAD DATA === " + style.RESET)

    def handle(self, *args, **options):
        self.load_data_log_backup_database()
