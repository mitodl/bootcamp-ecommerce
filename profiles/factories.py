"""
Factory for Profiles
"""
from django.contrib.auth.models import User
from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from profiles.models import Profile


class UserFactory(DjangoModelFactory):
    """Factory for User"""
    username = Sequence(lambda n: "user_%d" % n)
    email = FuzzyText(suffix='@example.com')

    class Meta:
        model = User


class ProfileFactory(DjangoModelFactory):
    """Factory for Profile"""
    user = SubFactory(UserFactory)
    name = Faker('name')

    class Meta:
        model = Profile
