"""
Factory for Profiles
"""
import string
from django.contrib.auth.models import User
from factory import Faker, Sequence, SubFactory, Trait, RelatedFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyChoice
from social_django.models import UserSocialAuth

from profiles.constants import (
    GENDER_CHOICES,
    COMPANY_SIZE_CHOICES,
    YRS_EXPERIENCE_CHOICES,
    HIGHEST_EDUCATION_CHOICES,
)
from profiles.models import Profile, LegalAddress


class UserFactory(DjangoModelFactory):
    """Factory for User"""

    username = Sequence(lambda n: "user_%d" % n)
    email = FuzzyText(suffix="@example.com")
    profile = RelatedFactory("profiles.factories.ProfileFactory", "user")
    legal_address = RelatedFactory("profiles.factories.LegalAddressFactory", "user")

    class Meta:
        model = User


class UserSocialAuthFactory(DjangoModelFactory):
    """Factory for UserSocialAuth"""

    provider = FuzzyText()
    user = SubFactory("profiles.factories.UserFactory")
    uid = FuzzyText()

    class Meta:
        model = UserSocialAuth


class LegalAddressFactory(DjangoModelFactory):
    """Factory for LegalAddress"""

    user = SubFactory("profiles.factories.UserFactory", legal_address=None)

    first_name = Faker("first_name")
    last_name = Faker("last_name")

    street_address_1 = Faker("street_address")

    state_or_territory = Faker("lexify", text="??-??", letters=string.ascii_uppercase)
    city = Faker("city")
    country = Faker("country_code", representation="alpha-2")
    postal_code = Faker("postalcode")

    class Meta:
        model = LegalAddress

    class Params:
        incomplete = Trait(first_name="", country="", city="")


class ProfileFactory(DjangoModelFactory):
    """Factory for Profile"""

    user = SubFactory("profiles.factories.UserFactory", profile=None)
    name = Faker("name")

    gender = FuzzyChoice(choices=[gender[0] for gender in GENDER_CHOICES])
    birth_year = Faker("year")
    company = Faker("company")
    job_title = Faker("word")
    industry = Faker("word")
    job_function = Faker("word")

    company_size = FuzzyChoice(
        choices=[size[0] for size in COMPANY_SIZE_CHOICES if size[0]]
    )
    years_experience = FuzzyChoice(
        choices=[exp[0] for exp in YRS_EXPERIENCE_CHOICES if exp[0]]
    )
    highest_education = FuzzyChoice(
        choices=[ed[0] for ed in HIGHEST_EDUCATION_CHOICES if ed[0]]
    )

    class Meta:
        model = Profile

    class Params:
        incomplete = Trait(job_title="", company="", gender="", birth_year=None)
