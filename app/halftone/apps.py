from django.apps import AppConfig


class HalftoneConfig(AppConfig):
    name = 'app.halftone'
    verbose_name = 'TrioStudio - Halftone DTF'

    def ready(self):
        # Import signals so they get registered.
        from app.halftone import signals  # noqa: F401
