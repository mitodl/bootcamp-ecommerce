"""Functions for testing ecommerce"""
from unittest.mock import patch

from applications.constants import AppStates
from backends.pipeline_api import EdxOrgOAuth2
from ecommerce.api import create_unfulfilled_order
from ecommerce.factories import BootcampApplicationFactory
from ecommerce.models import Order
from klasses.factories import InstallmentFactory
from profiles.factories import ProfileFactory


def create_test_application():
    """Create a purchasable bootcamp run, and a user to be associated with it"""
    profile = ProfileFactory.create()
    user = profile.user
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid="{}_edx".format(user.username),
    )
    installment_1 = InstallmentFactory.create(amount=200)
    bootcamp_run = installment_1.bootcamp_run
    InstallmentFactory.create(bootcamp_run=bootcamp_run)
    application = BootcampApplicationFactory.create(
        user=user,
        bootcamp_run=bootcamp_run,
        state=AppStates.AWAITING_PAYMENT.value,
    )
    return application


def create_purchasable_bootcamp_run():
    """A pair of (bootcamp run, user)"""
    application = create_test_application()
    return application.bootcamp_run, application.user


def create_test_order(application, payment, *, fulfilled):
    """
    Pass through arguments to create_unfulfilled_order and mock payable_bootcamp_run_keys
    """
    run_key = application.bootcamp_run.run_key
    user = application.user
    with patch(
        'ecommerce.api.payable_bootcamp_run_keys',
        return_value=[run_key],
    ):
        order = create_unfulfilled_order(user, run_key, payment)
    order.application = application
    if fulfilled:
        order.status = Order.FULFILLED
    order.save()
    return order
