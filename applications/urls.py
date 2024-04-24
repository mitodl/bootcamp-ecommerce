"""
URLs for bootcamp applications
"""

from django.urls import path
from django.urls import re_path, include
from rest_framework import routers

from applications.views import (
    BootcampApplicationViewset,
    ReviewSubmissionViewSet,
    LettersView,
    UploadResumeView,
)

router = routers.SimpleRouter()
router.register(
    r"applications", BootcampApplicationViewset, basename="applications_api"
)
router.register(r"submissions", ReviewSubmissionViewSet, basename="submissions_api")

urlpatterns = [
    re_path(r"^api/", include(router.urls)),
    re_path(
        r"^api/applications/(?P<pk>\d+)/resume/$",
        UploadResumeView.as_view(),
        name="upload-resume",
    ),
    path("letters/<uuid:hash>/", LettersView.as_view(), name="letters"),
]
