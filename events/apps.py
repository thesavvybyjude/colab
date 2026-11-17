from django.apps import AppConfig
from django.db.models.signals import post_migrate


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"
    verbose_name = "Programme"

    def ready(self):
        from .db_guards import on_post_migrate

        post_migrate.connect(on_post_migrate, sender=self)
