"""
URLs for ecommerce
"""

from django.urls import path, re_path

from ecommerce.views import (
    CheckoutDataView,
    OrderFulfillmentView,
    OrderView,
    PaymentView,
    UserBootcampRunDetail,
    UserBootcampRunList,
    UserBootcampRunStatement,
)

urlpatterns = [
    path("api/v0/payment/", PaymentView.as_view(), name="create-payment"),
    path(
        "api/v0/order_fulfillment/",
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
    path(
        "statement/<int:run_key>/",
        UserBootcampRunStatement.as_view(),
        name="bootcamp-run-statement",
    ),
    path("api/orders/<int:pk>/", OrderView.as_view(), name="order-api"),
    path("api/checkout/", CheckoutDataView.as_view(), name="checkout-data-detail"),
]
