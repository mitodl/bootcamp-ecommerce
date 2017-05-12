"""
URLs for klasses
"""
from django.conf.urls import url

from klasses.views import (
    UserKlassList,
    UserKlassDetail,
    UserKlassStatement,
)


urlpatterns = [
    url(r'^api/v0/klasses/(?P<username>[-\w.]+)/$', UserKlassList.as_view(), name='klass-list'),
    url(
        r'^api/v0/klasses/(?P<username>[-\w.]+)/(?P<klass_key>[\d]+)/$',
        UserKlassDetail.as_view(),
        name='klass-detail'
    ),
    url(r'^statement/(?P<klass_key>[0-9]+)/$', UserKlassStatement.as_view(), name='klass-statement'),
]
