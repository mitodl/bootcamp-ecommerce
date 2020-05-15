"""
URLs for ecommerce
"""
from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers

from ecommerce.views import (
    CheckoutDataViewSet,
    OrderFulfillmentView,
    PaymentView,
    UserBootcampRunDetail,
    UserBootcampRunList,
    UserBootcampRunStatement,
)

router = routers.DefaultRouter()
router.register("checkout", CheckoutDataViewSet, "checkout-data")


urlpatterns = [
    url(r'^api/v0/payment/$', PaymentView.as_view(), name='create-payment'),
    url(r'^api/v0/order_fulfillment/$', OrderFulfillmentView.as_view(), name='order-fulfillment'),
    url(r'^api/v0/bootcamps/(?P<username>[-\w.]+)/$', UserBootcampRunList.as_view(), name='bootcamp-run-list'),
    url(
        r'^api/v0/bootcamps/(?P<username>[-\w.]+)/(?P<run_key>[\d]+)/$',
        UserBootcampRunDetail.as_view(),
        name='bootcamp-run-detail'
    ),
    url(r'statement/(?P<run_key>[0-9]+)/$', UserBootcampRunStatement.as_view(), name='bootcamp-run-statement'),
    path("api/", include(router.urls))
]
