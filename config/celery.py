"""
Celery entry point for TrioStudio.

The Celery worker is started via:
    celery -A config worker -l info
"""
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('triostudio')

# Pull `CELERY_*` settings from Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py inside every installed Django app.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):  # pragma: no cover
    print(f'Request: {self.request!r}')
