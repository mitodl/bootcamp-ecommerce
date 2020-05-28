"""
URLs for bootcamp applications
"""
from django.conf.urls import url, include
from rest_framework import routers

from applications.views import BootcampApplicationViewset, ReviewSubmissionView

router = routers.SimpleRouter()
router.register(
    r"applications", BootcampApplicationViewset, basename="applications_api"
)

urlpatterns = [
    url(r"^api/", include(router.urls)),
    url(
        r"^api/submissions/(?P<pk>\d+)/$",
        ReviewSubmissionView.as_view(),
        name="submit-review",
    ),
]
