from django.apps import AppConfig


class TransversalConfig(AppConfig):
    name = 'app.transversal'

    def ready(self):
        import app.transversal.signals
