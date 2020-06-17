"""Factories for jobma models"""
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from factory.fuzzy import FuzzyInteger, FuzzyText

from jobma.models import Interview, Job
from klasses.factories import BootcampRunFactory


class JobFactory(DjangoModelFactory):
    """Factory for Job"""

    job_id = FuzzyInteger(10, 12345)
    job_code = FuzzyText()
    job_title = FuzzyText()
    interview_template_id = FuzzyInteger(10, 12345)
    run = SubFactory(BootcampRunFactory)

    class Meta:
        model = Job


class InterviewFactory(DjangoModelFactory):
    """Factory for Interview"""

    job = SubFactory(JobFactory)
    interview_url = Faker("url")
    applicant = SubFactory("profiles.factories.UserFactory")

    class Meta:
        model = Interview
