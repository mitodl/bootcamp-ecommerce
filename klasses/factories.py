"""
Factories for bootcamp models
"""

import random
from factory import Faker, Sequence, SubFactory, LazyAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyDecimal, FuzzyText
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


class BootcampRunFactory(DjangoModelFactory):
    """Factory for BootcampRun"""

    title = FuzzyText(prefix="Bootcamp run ")
    bootcamp = SubFactory(BootcampFactory)
    run_key = Sequence(lambda n: n)
    start_date = Faker(
        "date_time_this_year", before_now=True, after_now=False, tzinfo=pytz.UTC
    )
    end_date = Faker(
        "date_time_this_year", before_now=False, after_now=True, tzinfo=pytz.UTC
    )
    novoed_course_stub = LazyAttribute(
        lambda bootcamp_run: "-".join(bootcamp_run.title.lower().split(" "))[0:20]
    )
    bootcamp_run_id = LazyAttribute(
        lambda bootcamp_run: "bootcamp-v1:{type}+{topic}-{format}+R{run}".format(
            type=random.choice(["public", "private"]),
            topic="".join([word[0] for word in bootcamp_run.title.split()]).upper(),
            format=random.choice(["ol", "f2f"]),
            run=bootcamp_run.run_key,
        )[0:255]
    )

    class Meta:
        model = models.BootcampRun


class BootcampRunEnrollmentFactory(DjangoModelFactory):
    """Factory for BootcampRunEnrollment"""

    user = SubFactory(UserFactory)
    bootcamp_run = SubFactory(BootcampRunFactory)

    class Meta:
        model = models.BootcampRunEnrollment


class InstallmentFactory(DjangoModelFactory):
    """Factory for Installment"""

    bootcamp_run = SubFactory(BootcampRunFactory)
    amount = FuzzyDecimal(low=1, high=2000)
    deadline = Faker(
        "date_time_this_month", before_now=False, after_now=True, tzinfo=pytz.UTC
    )

    class Meta:
        model = models.Installment


class PersonalPriceFactory(DjangoModelFactory):
    """Factory for PersonalPrice"""

    bootcamp_run = SubFactory(BootcampRunFactory)
    user = SubFactory(UserFactory)
    price = FuzzyDecimal(low=1, high=2000)

    class Meta:
        model = models.PersonalPrice


class BootcampRunCertificateFactory(DjangoModelFactory):
    """Factory for BootcampRunCertificate"""

    user = SubFactory(UserFactory)
    bootcamp_run = SubFactory(BootcampRunFactory)

    class Meta:
        model = models.BootcampRunCertificate
