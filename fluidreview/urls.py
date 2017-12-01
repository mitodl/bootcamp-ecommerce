"""URLs for fluidreview"""

from django.conf.urls import url

from fluidreview.views import WebhookView


urlpatterns = [
    url(r'^api/v0/fluidreview_webhook/$', WebhookView.as_view(), name='fluidreview-webhook'),
]
