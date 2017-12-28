"""
Django App
"""
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


class BootcampConfig(AppConfig):
    """AppConfig for Bootcamp"""
    name = 'bootcamp'

    def ready(self):
        # check for missing configurations
        from django.conf import settings
        missing_settings = []
        for setting_name in settings.MANDATORY_SETTINGS:
            if getattr(settings, setting_name, None) in (None, '',):
                missing_settings.append(setting_name)
        if missing_settings:
            raise ImproperlyConfigured(
                'The following settings are missing: {}'.format(', '.join(missing_settings)))
