"""Factories for jobma models"""
from factory import SubFactory
from factory.django import DjangoModelFactory

from factory.fuzzy import (
    FuzzyInteger,
    FuzzyText,
)

from jobma.models import Interview, Job
from klasses.factories import KlassFactory


class JobFactory(DjangoModelFactory):
    """Factory for Job"""
    job_id = FuzzyInteger(10, 12345)
    job_code = FuzzyText()
    job_title = FuzzyText()
    interview_template_id = FuzzyInteger(10, 12345)
    run = SubFactory(KlassFactory)

    class Meta:
        model = Job


class InterviewFactory(DjangoModelFactory):
    """Factory for Interview"""
    job = SubFactory(JobFactory)
    interview_id = None
    candidate_first_name = FuzzyText()
    candidate_last_name = FuzzyText()
    candidate_phone = Faker("phone_number)
    candidate_email = Faker("email")

    class Meta:
        model = Interview
