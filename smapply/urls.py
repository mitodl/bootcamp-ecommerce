"""URLs for smapply"""

from django.conf.urls import url

from smapply.views import WebhookView


urlpatterns = [
    url(r'^api/v0/smapply_webhook/$', WebhookView.as_view(), name='smapply-webhook'),
]
