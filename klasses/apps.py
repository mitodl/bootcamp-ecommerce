"""Bootcamp app definition (called 'klasses' for legacy reasons)"""

from django.apps import AppConfig


class KlassesConfig(AppConfig):
    """AppConfig for klasses"""

    name = "klasses"

    def ready(self):
        """Application is ready"""
        import klasses.signals  # noqa: F401
