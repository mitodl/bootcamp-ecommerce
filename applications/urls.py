"""
URLs for bootcamp applications
"""

from django.urls import path
from django.urls import include
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
    path("api/", include(router.urls)),
    path(
        "api/applications/<int:pk>/resume/",
        UploadResumeView.as_view(),
        name="upload-resume",
    ),
    path("letters/<uuid:hash>/", LettersView.as_view(), name="letters"),
]
