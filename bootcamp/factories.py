"""
Factory for Users
"""
from django.contrib.auth.models import User
from factory import Faker, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class UserFactory(DjangoModelFactory):
    """Factory for Users"""
    username = Sequence(lambda n: "user_%d" % n)
    email = FuzzyText(suffix='@example.com')
    first_name = Faker('first_name')
    last_name = Faker('last_name')

    class Meta:
        model = User
