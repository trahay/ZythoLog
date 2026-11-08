from django.apps import AppConfig


class TastingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tastings"
    verbose_name = "Dégustations"

    def ready(self):
        from . import signals  # noqa: F401
