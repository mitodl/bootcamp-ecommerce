"""
URLs for bootcamps
"""
from django.conf.urls import url

from klasses.views import (
    UserBootcampRunList,
    UserBootcampRunDetail,
    UserBootcampRunStatement,
)


urlpatterns = [
    url(r'^api/v0/bootcamps/(?P<username>[-\w.]+)/$', UserBootcampRunList.as_view(), name='bootcamp-run-list'),
    url(
        r'^api/v0/bootcamps/(?P<username>[-\w.]+)/(?P<run_key>[\d]+)/$',
        UserBootcampRunDetail.as_view(),
        name='bootcamp-run-detail'
    ),
    url(r'^statement/(?P<run_key>[0-9]+)/$', UserBootcampRunStatement.as_view(), name='bootcamp-run-statement'),
]
