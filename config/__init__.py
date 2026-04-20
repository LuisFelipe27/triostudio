from __future__ import absolute_import, unicode_literals

# Make sure the Celery app is loaded when Django starts so that
# `shared_task` decorators bind correctly.
from .celery import app as celery_app

__all__ = ('celery_app',)
