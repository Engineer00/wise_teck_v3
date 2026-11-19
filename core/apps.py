from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Website content"

    def ready(self):
        from . import images, signals  # noqa: F401  (shrink new photo uploads; redirect changed addresses)
