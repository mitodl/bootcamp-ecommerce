"""
Factories for ecommerce models
"""
from factory import (
    Faker,
    SubFactory,
)
from factory.django import DjangoModelFactory
from factory.fuzzy import (
    FuzzyDecimal,
    FuzzyInteger,
    FuzzyText,
)
import faker
import pytz

from klasses.models import (
    Bootcamp,
    Installment,
    Klass,
)


FAKE = faker.Factory.create()


class BootcampFactory(DjangoModelFactory):
    """Factory for Bootcamp"""
    title = FuzzyText(prefix="Bootcamp ")

    class Meta:
        model = Bootcamp


class KlassFactory(DjangoModelFactory):
    """Factory for Klass"""
    title = FuzzyText(prefix="Klass ")
    bootcamp = SubFactory(BootcampFactory)
    klass_id = FuzzyInteger(low=1, high=1234)
    start_date = Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    end_date = Faker('date_time_this_year', before_now=False, after_now=True, tzinfo=pytz.UTC)

    class Meta:
        model = Klass


class InstallmentFactory(DjangoModelFactory):
    """Factory for Installment"""
    klass = SubFactory(KlassFactory)
    installment_number = FuzzyInteger(low=1, high=1234)
    min_amount = FuzzyDecimal(low=1, high=2000)
    deadline = Faker('date_time_this_month', before_now=False, after_now=True, tzinfo=pytz.UTC)

    class Meta:
        model = Installment
