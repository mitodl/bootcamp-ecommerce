"""SMApply app definition"""
from django.apps import AppConfig


class SMApplyConfig(AppConfig):
    """
    AppConfig for SMApply
    """
    name = 'smapply'

    def ready(self):
        """
        Ready handler. Import signals.
        """
        import smapply.signals  # pylint: disable=unused-variable
