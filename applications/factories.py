"""
Factories for bootcamp application models
"""
import operator as op
from factory import Faker, LazyAttribute, Sequence, SubFactory, fuzzy, Trait
from factory.django import DjangoModelFactory
import faker
import pytz

from applications import models
from applications.constants import (
    VALID_SUBMISSION_TYPE_CHOICES,
    VALID_APP_STATE_CHOICES,
    ALL_REVIEW_STATUSES,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_WAITLISTED,
    ALL_LETTER_TYPES,
    SUBMISSION_STATUS_SUBMITTED,
    REVIEWABLE_APP_STATES,
)
from jobma.factories import InterviewFactory
from klasses.factories import BootcampFactory, BootcampRunFactory
from main.utils import now_in_utc
from profiles.factories import UserFactory

FAKE = faker.Factory.create()


class ApplicationStepFactory(DjangoModelFactory):
    """Factory for ApplicationStep"""

    bootcamp = SubFactory(BootcampFactory)
    step_order = Sequence(lambda n: n)
    submission_type = fuzzy.FuzzyChoice(
        choices=list(map(op.itemgetter(0), VALID_SUBMISSION_TYPE_CHOICES))
    )

    class Meta:
        model = models.ApplicationStep


class BootcampRunApplicationStepFactory(DjangoModelFactory):
    """Factory for BootcampRunApplicationStep"""

    bootcamp_run = SubFactory(BootcampRunFactory)
    application_step = SubFactory(ApplicationStepFactory)
    due_date = Faker(
        "date_time_this_year", before_now=False, after_now=True, tzinfo=pytz.UTC
    )

    class Meta:
        model = models.BootcampRunApplicationStep


class BootcampApplicationFactory(DjangoModelFactory):
    """Factory for BootcampApplication"""

    user = SubFactory(UserFactory)
    bootcamp_run = SubFactory(BootcampRunFactory)
    resume_file = None
    resume_upload_date = fuzzy.FuzzyDateTime(start_dt=now_in_utc())
    state = fuzzy.FuzzyChoice(
        choices=list(map(op.itemgetter(0), VALID_APP_STATE_CHOICES))
    )
    linkedin_url = Faker("url")

    class Meta:
        model = models.BootcampApplication


class VideoInterviewSubmissionFactory(DjangoModelFactory):
    """Factory for VideoInterviewSubmission"""

    interview = SubFactory(InterviewFactory)

    class Meta:
        model = models.VideoInterviewSubmission


class QuizSubmissionFactory(DjangoModelFactory):
    """Factory for QuizSubmission"""

    started_date = fuzzy.FuzzyDateTime(start_dt=now_in_utc())

    class Meta:
        model = models.QuizSubmission


class ApplicationStepSubmissionFactory(DjangoModelFactory):
    """Factory for ApplicationStepSubmission"""

    content_object = SubFactory(VideoInterviewSubmissionFactory)
    bootcamp_application = SubFactory(BootcampApplicationFactory)
    run_application_step = LazyAttribute(
        lambda _self: BootcampRunApplicationStepFactory(
            bootcamp_run=_self.bootcamp_application.bootcamp_run
        )
    )
    submitted_date = fuzzy.FuzzyDateTime(start_dt=now_in_utc())
    review_status = fuzzy.FuzzyChoice(choices=ALL_REVIEW_STATUSES)
    review_status_date = fuzzy.FuzzyDateTime(start_dt=now_in_utc())

    class Params:
        is_pending = Trait(review_status=REVIEW_STATUS_PENDING)
        is_rejected = Trait(review_status=REVIEW_STATUS_REJECTED)
        is_approved = Trait(review_status=REVIEW_STATUS_APPROVED)
        is_waitlisted = Trait(review_status=REVIEW_STATUS_WAITLISTED)

        is_review_ready = Trait(
            submission_status=SUBMISSION_STATUS_SUBMITTED,
            bootcamp_application__state=fuzzy.FuzzyChoice(REVIEWABLE_APP_STATES),
        )

    class Meta:
        model = models.ApplicationStepSubmission


class ApplicantLetterFactory(DjangoModelFactory):
    """Factory for ApplicantLetter"""

    application = SubFactory(BootcampApplicationFactory)
    letter_text = fuzzy.FuzzyText()
    letter_subject = fuzzy.FuzzyText()
    letter_type = fuzzy.FuzzyChoice(choices=ALL_LETTER_TYPES)

    class Meta:
        model = models.ApplicantLetter
