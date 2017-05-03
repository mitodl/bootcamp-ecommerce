"""Tests for klass related models"""
from datetime import datetime
from pytz import utc
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

    def test_payment_deadline(self):
        """Price should be sum total of all installments for that klass"""
        installment_1 = InstallmentFactory.create(deadline=None)
        klass = installment_1.klass
        InstallmentFactory.create(
            klass=klass,
            deadline=datetime(year=2017, month=1, day=1, tzinfo=utc)
        )
        installment_2 = InstallmentFactory.create(
            klass=klass,
            deadline=datetime(year=2017, month=2, day=1, tzinfo=utc)
        )

        assert klass.payment_deadline == installment_2.deadline
