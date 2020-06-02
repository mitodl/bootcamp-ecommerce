"""
URLs for bootcamp applications
"""
from django.conf.urls import url, include
from rest_framework import routers

from applications.views import (
    BootcampApplicationViewset,
    ReviewSubmissionViewSet,
    UploadResumeView,
)

router = routers.SimpleRouter()
router.register(
    r"applications", BootcampApplicationViewset, basename="applications_api"
)
router.register(r"submissions", ReviewSubmissionViewSet, basename="submissions_api")

urlpatterns = [
    url(r"^api/", include(router.urls)),
    url(
        r"^api/applications/(?P<pk>\d+)/resume/$",
        UploadResumeView.as_view(),
        name="upload-resume",
    ),
]
