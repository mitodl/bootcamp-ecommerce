"""urls for jobma"""

from django.urls import path

from jobma.views import JobmaWebhookView

urlpatterns = [
    path(
        "api/v0/jobma_webhook/<int:pk>/",
        JobmaWebhookView.as_view(),
        name="jobma-webhook",
    )
]
