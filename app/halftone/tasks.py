"""Celery tasks for the TrioStudio halftone pipeline.

Tasks are tenant-aware: the calling view passes the schema name so the
worker can switch into the correct PostgreSQL schema before touching the
ORM. This keeps the stack compatible with django-tenant-schemas.
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.core.files.base import ContentFile
from django.db import connection
from PIL import Image

from app.halftone import processing
from app.halftone.models import HalftoneJob

logger = logging.getLogger(__name__)


def _switch_schema(schema_name):
    """Switch the connection to the requested tenant schema if provided."""
    if not schema_name:
        return
    try:
        from tenant_schemas.utils import schema_context
        return schema_context(schema_name)
    except Exception:  # pragma: no cover - safe fallback
        logger.warning('Tenant schema switch failed for %s', schema_name)
        return None


def _run_with_schema(schema_name, func):
    ctx = _switch_schema(schema_name)
    if ctx is None:
        return func()
    with ctx:
        return func()


@shared_task(bind=True, max_retries=2, default_retry_delay=5)
def process_halftone(self, job_id, mode='preview', schema_name=None):
    """Render either the preview or the export image for a HalftoneJob."""

    def _work():
        try:
            job = HalftoneJob.objects.get(pk=job_id)
        except HalftoneJob.DoesNotExist:
            logger.warning('HalftoneJob %s missing in schema %s', job_id, connection.schema_name)
            return

        job.status = HalftoneJob.STATUS_PROCESSING
        job.last_mode = mode
        job.error_message = ''
        job.save(update_fields=['status', 'last_mode', 'error_message', 'modified'])

        try:
            params = processing.HalftoneParams.from_model(job)
            with Image.open(job.original.path) as src:
                src.load()
                if mode == HalftoneJob.MODE_EXPORT:
                    result = processing.render_export(src, params)
                    payload = processing.image_to_png_bytes(result, dpi=params.export_dpi)
                    job.export.save('export.png', ContentFile(payload), save=False)
                else:
                    result = processing.render_preview(src, params)
                    payload = processing.image_to_png_bytes(result)
                    job.preview.save('preview.png', ContentFile(payload), save=False)

            job.status = HalftoneJob.STATUS_DONE
            job.save()
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception('Halftone processing failed for job %s', job_id)
            job.status = HalftoneJob.STATUS_ERROR
            job.error_message = str(exc)[:2000]
            job.save(update_fields=['status', 'error_message', 'modified'])
            raise

    return _run_with_schema(schema_name, _work)
