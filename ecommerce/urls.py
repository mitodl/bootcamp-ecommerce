"""
URLs for bootcamp
"""
from django.conf.urls import url

from ecommerce.views import (
    PaymentView,
)


urlpatterns = [
    url(r'^api/v0/payment/$', PaymentView.as_view(), name='create-payment'),
]
