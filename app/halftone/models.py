"""
TrioStudio - Halftone module models.

A `HalftoneJob` represents an image upload + a set of halftone parameters.
Image processing is done asynchronously through Celery; the job tracks
status so the front-end (HTMX polling) can pick up the result.
"""
import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def _upload_to_original(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    return f'halftone/{instance.uid}/original{ext}'


def _upload_to_preview(instance, filename):
    return f'halftone/{instance.uid}/preview.png'


def _upload_to_export(instance, filename):
    return f'halftone/{instance.uid}/export.png'


class HalftoneJob(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_DONE = 'done'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = (
        (STATUS_PENDING, _('Pendiente')),
        (STATUS_PROCESSING, _('Procesando')),
        (STATUS_DONE, _('Listo')),
        (STATUS_ERROR, _('Error')),
    )

    SHAPE_CIRCLE = 'circle'
    SHAPE_LINES = 'lines'
    SHAPE_CHOICES = (
        (SHAPE_CIRCLE, _('Círculo')),
        (SHAPE_LINES, _('Líneas')),
    )

    MODE_PREVIEW = 'preview'
    MODE_EXPORT = 'export'

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='halftone_jobs'
    )

    # Source / outputs
    original = models.ImageField(_('Imagen original'), upload_to=_upload_to_original)
    preview = models.ImageField(
        _('Vista previa'), upload_to=_upload_to_preview, blank=True, null=True
    )
    export = models.FileField(
        _('Exportación final'), upload_to=_upload_to_export, blank=True, null=True
    )

    # --- Halftone parameters (mirrors the UI in the screenshot) ---
    knockout_enable = models.BooleanField(_('Knockout habilitado'), default=True)
    knockout_color = models.CharField(_('Color knockout'), max_length=9, default='#000000')
    bg_color = models.CharField(_('Color de fondo'), max_length=9, default='#FFFFFF')

    dot_shape = models.CharField(
        _('Forma del punto'), max_length=10, choices=SHAPE_CHOICES, default=SHAPE_CIRCLE
    )
    dot_size = models.FloatField(_('Tamaño del punto (px)'), default=6.0)
    dot_angle = models.FloatField(_('Ángulo del punto (°)'), default=45.0)

    print_width_cm = models.FloatField(_('Ancho de impresión (cm)'), default=25.0)
    export_dpi = models.PositiveIntegerField(_('DPI de exportación'), default=300)

    contrast_boost = models.FloatField(_('Contraste'), default=1.2)

    # Advanced: pre-processing
    blur = models.FloatField(_('Desenfoque (px)'), default=0.0)
    gamma = models.FloatField(_('Gamma'), default=1.0)

    # Advanced: tonal balance
    gradient_intensity = models.FloatField(_('Intensidad de gradiente'), default=0.8)
    brightness = models.FloatField(_('Brillo'), default=0.0)

    # --- Status tracking ---
    status = models.CharField(
        _('Estado'), max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    last_mode = models.CharField(_('Último modo'), max_length=10, default=MODE_PREVIEW)
    error_message = models.TextField(_('Mensaje de error'), blank=True, default='')

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Trabajo de semitono')
        verbose_name_plural = _('Trabajos de semitono')
        ordering = ('-created',)

    def __str__(self):
        return f'HalftoneJob<{self.uid}> [{self.status}]'

    # --- Convenience helpers ---
    @property
    def is_processing(self):
        return self.status in (self.STATUS_PENDING, self.STATUS_PROCESSING)

    @property
    def is_done(self):
        return self.status == self.STATUS_DONE

    def update_params(self, data):
        """Bulk-assign halftone parameters from a cleaned form/dict."""
        fields = (
            'knockout_enable', 'knockout_color', 'bg_color',
            'dot_shape', 'dot_size', 'dot_angle',
            'print_width_cm', 'export_dpi', 'contrast_boost',
        )
        for f in fields:
            if f in data and data[f] is not None:
                setattr(self, f, data[f])
