"""
URLs for bootcamp
"""
from django.conf.urls import include, url
from bootcamp.views import index


urlpatterns = [
    url(r'^$', index, name='bootcamp-index'),
    url(r'^status/', include('server_status.urls')),
]
