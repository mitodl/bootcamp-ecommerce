"""
Django App
"""

from mitol.common import envs
from mitol.common.apps import BaseApp


class MainAppConfig(BaseApp):
    """AppConfig for main app"""

    name = "main"

    def ready(self):
        # check for missing configurations

        envs.validate()
