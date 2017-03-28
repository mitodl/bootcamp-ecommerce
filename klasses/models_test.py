"""Tests for klass related models"""
from django.test import TestCase

from klasses.factories import InstallmentFactory


class KlassesTests(TestCase):
    """
    Tests for Klass and related models
    """

    def test_price(self):
        """Price should be sum total of all installments for that klass"""
        installment_1 = InstallmentFactory.create()
        klass = installment_1.klass
        installment_2 = InstallmentFactory.create(klass=klass)
        # Create an unrelated installment to show that it doesn't affect the price
        InstallmentFactory.create()

        assert klass.price == installment_1.amount + installment_2.amount
