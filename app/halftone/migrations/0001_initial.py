import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import app.halftone.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HalftoneJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('original', models.ImageField(upload_to=app.halftone.models._upload_to_original, verbose_name='Imagen original')),
                ('preview', models.ImageField(blank=True, null=True, upload_to=app.halftone.models._upload_to_preview, verbose_name='Vista previa')),
                ('export', models.FileField(blank=True, null=True, upload_to=app.halftone.models._upload_to_export, verbose_name='Exportación final')),
                ('knockout_enable', models.BooleanField(default=True, verbose_name='Knockout habilitado')),
                ('knockout_color', models.CharField(default='#000000', max_length=9, verbose_name='Color knockout')),
                ('bg_color', models.CharField(default='#FFFFFF', max_length=9, verbose_name='Color de fondo')),
                ('dot_shape', models.CharField(choices=[('circle', 'Círculo'), ('lines', 'Líneas')], default='circle', max_length=10, verbose_name='Forma del punto')),
                ('dot_size', models.FloatField(default=10.0, verbose_name='Tamaño del punto (px)')),
                ('dot_angle', models.FloatField(default=45.0, verbose_name='Ángulo del punto (°)')),
                ('print_width_cm', models.FloatField(default=25.0, verbose_name='Ancho de impresión (cm)')),
                ('export_dpi', models.PositiveIntegerField(default=300, verbose_name='DPI de exportación')),
                ('contrast_boost', models.FloatField(default=1.2, verbose_name='Refuerzo de contraste')),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('processing', 'Procesando'), ('done', 'Listo'), ('error', 'Error')], default='pending', max_length=12, verbose_name='Estado')),
                ('last_mode', models.CharField(default='preview', max_length=10, verbose_name='Último modo')),
                ('error_message', models.TextField(blank=True, default='', verbose_name='Mensaje de error')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='halftone_jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Trabajo de semitono',
                'verbose_name_plural': 'Trabajos de semitono',
                'ordering': ('-created',),
            },
        ),
    ]
