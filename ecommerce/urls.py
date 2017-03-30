"""
URLs for bootcamp
"""
from django.conf.urls import url

from ecommerce.views import (
    OrderFulfillmentView,
    PaymentView,
)


urlpatterns = [
    url(r'^api/v0/payment/$', PaymentView.as_view(), name='create-payment'),
    url(r'^api/v0/order_fulfillment/$', OrderFulfillmentView.as_view(), name='order-fulfillment'),
]
