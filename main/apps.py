"""
Django App
"""
from django.apps import AppConfig


class MainAppConfig(AppConfig):
    """AppConfig for main app"""
    name = 'main'

    def ready(self):
        # check for missing configurations
        from main import envs

        envs.validate()
