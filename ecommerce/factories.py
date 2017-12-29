"""
Factories for ecommerce models
"""
from factory import (
    LazyAttribute,
    SelfAttribute,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory
from factory.fuzzy import (
    FuzzyChoice,
    FuzzyDecimal,
    FuzzyInteger,
    FuzzyText,
)
import faker

from ecommerce.api import (
    make_reference_id,
    generate_cybersource_sa_signature,
)
from ecommerce.models import (
    Line,
    Order,
    Receipt,
)
from profiles.factories import UserFactory


FAKE = faker.Factory.create()


class OrderFactory(DjangoModelFactory):
    """Factory for Order"""
    user = SubFactory(UserFactory)
    status = FuzzyChoice(
        Order.STATUSES
    )
    total_price_paid = FuzzyDecimal(low=0, high=12345)

    class Meta:
        model = Order


class LineFactory(DjangoModelFactory):
    """Factory for Line"""
    order = SubFactory(OrderFactory)
    price = SelfAttribute('order.total_price_paid')
    klass_key = Sequence(lambda n: n)
    description = FuzzyText(prefix="Line ")

    class Meta:
        model = Line


def gen_fake_receipt_data(order=None):
    """
    Helper function to generate a fake signed piece of data
    """
    data = {}
    for _ in range(10):
        data[FAKE.text()] = FAKE.text()
    keys = sorted(data.keys())
    data['signed_field_names'] = ",".join(keys)
    data['unsigned_field_names'] = ''
    data['req_reference_number'] = make_reference_id(order) if order else ''
    data['signature'] = generate_cybersource_sa_signature(data)
    return data


class ReceiptFactory(DjangoModelFactory):
    """Factory for Receipt"""
    order = SubFactory(OrderFactory)
    data = LazyAttribute(lambda receipt: gen_fake_receipt_data(receipt.order))

    class Meta:
        model = Receipt
