"""
Factories for ecommerce models
"""
from factory import (
    Faker,
    Sequence,
    SubFactory,
)
from factory.django import DjangoModelFactory
from factory.fuzzy import (
    FuzzyDecimal,
    FuzzyText
)
import faker
import pytz

from klasses import models
from profiles.factories import UserFactory

FAKE = faker.Factory.create()


class BootcampFactory(DjangoModelFactory):
    """Factory for Bootcamp"""
    title = FuzzyText(prefix="Bootcamp ")

    class Meta:
        model = models.Bootcamp


class KlassFactory(DjangoModelFactory):
    """Factory for Klass"""
    title = FuzzyText(prefix="Klass ")
    bootcamp = SubFactory(BootcampFactory)
    klass_key = Sequence(lambda n: n)
    start_date = Faker('date_time_this_year', before_now=True, after_now=False, tzinfo=pytz.UTC)
    end_date = Faker('date_time_this_year', before_now=False, after_now=True, tzinfo=pytz.UTC)

    class Meta:
        model = models.Klass


class InstallmentFactory(DjangoModelFactory):
    """Factory for Installment"""
    klass = SubFactory(KlassFactory)
    amount = FuzzyDecimal(low=1, high=2000)
    deadline = Faker('date_time_this_month', before_now=False, after_now=True, tzinfo=pytz.UTC)

    class Meta:
        model = models.Installment


class PersonalPriceFactory(DjangoModelFactory):
    """Factory for PersonalPrice"""
    klass = SubFactory(KlassFactory)
    user = SubFactory(UserFactory)
    price = FuzzyDecimal(low=1, high=2000)

    class Meta:
        model = models.PersonalPrice
