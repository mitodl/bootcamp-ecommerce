"""
URLs for klasses
"""
from django.conf.urls import url

from klasses.views import (
    UserKlassList,
    UserKlassDetail,
)


urlpatterns = [
    url(r'^api/v0/klasses/(?P<username>[-\w.]+)/$', UserKlassList.as_view(), name='klass-list'),
    url(
        r'^api/v0/klasses/(?P<username>[-\w.]+)/(?P<klass_key>[\d]+)/$',
        UserKlassDetail.as_view(),
        name='klass-detail'
    ),
]
