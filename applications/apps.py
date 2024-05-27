"""Apps for bootcamp applications"""

from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    """AppConfig for bootcamp applications"""

    name = "applications"

    def ready(self):
        """Application is ready"""
        import applications.signals  # noqa: F401
