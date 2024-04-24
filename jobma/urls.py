"""urls for jobma"""

from django.urls import re_path

from jobma.views import JobmaWebhookView

urlpatterns = [
    re_path(
        r"api/v0/jobma_webhook/(?P<pk>\d+)/$",
        JobmaWebhookView.as_view(),
        name="jobma-webhook",
    )
]
