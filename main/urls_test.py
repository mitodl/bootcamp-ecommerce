"""Tests for URLs"""
from django.urls import reverse


def test_urls():
    """Make sure URLs match with resolved names"""
    assert reverse("pay") == "/pay/"
    assert reverse("create-payment") == "/api/v0/payment/"
    assert reverse("order-fulfillment") == "/api/v0/order_fulfillment/"
