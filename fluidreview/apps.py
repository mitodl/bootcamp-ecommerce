"""Fluidreview app definition"""
from django.apps import AppConfig


class FluidReviewConfig(AppConfig):
    """
    AppConfig for FluidReview
    """
    name = 'fluidreview'

    def ready(self):
        """
        Ready handler. Import signals.
        """
        import fluidreview.signals  # pylint: disable=unused-variable
