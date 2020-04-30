"""urls for jobma"""
from django.conf.urls import url

from jobma.views import JobmaWebhookView

urlpatterns = [
    url(r"api/v0/jobma_webhook/(?P<pk>\d+)/$", JobmaWebhookView.as_view(), name='jobma-webhook'),
]
