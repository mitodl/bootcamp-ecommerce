"""
URLs for ecommerce
"""

from django.urls import re_path
from django.urls import path

from ecommerce.views import (
    CheckoutDataView,
    OrderFulfillmentView,
    PaymentView,
    UserBootcampRunDetail,
    UserBootcampRunList,
    UserBootcampRunStatement,
    OrderView,
)


urlpatterns = [
    re_path(r"^api/v0/payment/$", PaymentView.as_view(), name="create-payment"),
    re_path(
        r"^api/v0/order_fulfillment/$",
        OrderFulfillmentView.as_view(),
        name="order-fulfillment",
    ),
    re_path(
        r"^api/v0/bootcamps/(?P<username>[-\w.]+)/$",
        UserBootcampRunList.as_view(),
        name="bootcamp-run-list",
    ),
    re_path(
        r"^api/v0/bootcamps/(?P<username>[-\w.]+)/(?P<run_key>[\d]+)/$",
        UserBootcampRunDetail.as_view(),
        name="bootcamp-run-detail",
    ),
    re_path(
        r"statement/(?P<run_key>[0-9]+)/$",
        UserBootcampRunStatement.as_view(),
        name="bootcamp-run-statement",
    ),
    re_path(r"api/orders/(?P<pk>[0-9]+)/$", OrderView.as_view(), name="order-api"),
    path("api/checkout/", CheckoutDataView.as_view(), name="checkout-data-detail"),
]
