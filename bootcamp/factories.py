"""
Factory for Users
"""
from django.contrib.auth.models import User
from factory import Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class UserFactory(DjangoModelFactory):
    """Factory for Users"""
    username = Sequence(lambda n: "user_%d" % n)
    email = FuzzyText(suffix='@example.com')
    first_name = FuzzyText()
    last_name = FuzzyText()

    class Meta:
        model = User
