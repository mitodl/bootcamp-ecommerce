"""urls for bootcamps"""

from django.urls import path, include
from rest_framework import routers

from klasses.views import BootcampViewSet


router = routers.DefaultRouter()
router.register("bootcampruns", BootcampViewSet, "bootcamp-runs")

urlpatterns = [path("api/", include(router.urls))]
