from django.apps import AppConfig


class OpsConfig(AppConfig):
    name = 'ops'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import ops.signals.handlers
