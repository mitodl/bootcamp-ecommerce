"""Application management util tests"""
# pylint: disable=redefined-outer-name
from types import SimpleNamespace
import pytest
import factory
from django.core.exceptions import ValidationError

from django.core.files.uploadedfile import SimpleUploadedFile

from applications.api import derive_application_state
from applications.constants import (
    REVIEW_STATUS_APPROVED,
    SUBMISSION_VIDEO,
    AppStates,
    SUBMISSION_QUIZ,
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepFactory,
    ApplicationStepSubmissionFactory,
    VideoInterviewSubmissionFactory,
    QuizSubmissionFactory,
)
from applications.management.utils import (
    migrate_application,
    has_same_application_steps,
)
from ecommerce.factories import OrderFactory
from ecommerce.models import Order
from klasses.factories import BootcampFactory, BootcampRunFactory, InstallmentFactory
from main.utils import now_in_utc
from profiles.factories import UserFactory

FAKE_FILE_NAME = "file.txt"
FAKE_LINKEDIN_URL = "http://example.com/linkedin"
BOOTCAMP_PRICE = 100


@pytest.fixture()
def bootcamp_data():
    """Fixture for bootcamps data"""
    bootcamp = BootcampFactory.create()
    bootcamp_runs = BootcampRunFactory.create_batch(2, bootcamp=bootcamp)
    InstallmentFactory.create_batch(
        len(bootcamp_runs),
        amount=BOOTCAMP_PRICE,
        bootcamp_run=factory.Iterator(bootcamp_runs),
    )
    submission_types = [SUBMISSION_VIDEO, SUBMISSION_VIDEO, SUBMISSION_QUIZ]
    app_steps = ApplicationStepFactory.create_batch(
        len(submission_types),
        bootcamp=bootcamp,
        submission_type=factory.Iterator(submission_types),
        step_order=factory.Iterator([1, 2, 3]),
    )
    run_app_steps = {
        run.id: BootcampRunApplicationStepFactory.create_batch(
            len(app_steps),
            bootcamp_run=run,
            application_step=factory.Iterator(app_steps),
        )
        for run in bootcamp_runs
    }
    return SimpleNamespace(
        bootcamp=bootcamp,
        runs=bootcamp_runs,
        app_steps=app_steps,
        run_app_steps=run_app_steps,
        submission_types=submission_types,
    )


@pytest.fixture()
def completed_app_data(bootcamp_data):
    """Fixture with a completed bootcamp application and associated data"""
    user = UserFactory.create()
    run = bootcamp_data.runs[0]
    now = now_in_utc()
    application = BootcampApplicationFactory.create(
        user=user,
        bootcamp_run=run,
        resume_file=SimpleUploadedFile(
            f"path/to/{FAKE_FILE_NAME}", b"these are the file contents"
        ),
        linkedin_url=FAKE_LINKEDIN_URL,
        resume_upload_date=now,
    )
    submissions = ApplicationStepSubmissionFactory.create_batch(
        run.application_steps.count(),
        bootcamp_application=application,
        run_application_step=factory.Iterator(
            run.application_steps.order_by("application_step__step_order").all()
        ),
        content_object=factory.Iterator(
            [
                VideoInterviewSubmissionFactory.create(),
                VideoInterviewSubmissionFactory.create(),
                QuizSubmissionFactory.create(),
            ]
        ),
        submitted_date=now,
        review_status=REVIEW_STATUS_APPROVED,
        review_status_date=now,
    )
    order = OrderFactory.create(
        application=application,
        user=user,
        status=Order.FULFILLED,
        total_price_paid=BOOTCAMP_PRICE,
    )
    application.state = derive_application_state(application)
    application.save()
    return SimpleNamespace(
        application=application, submissions=submissions, order=order
    )


@pytest.mark.django_db
def test_migrate_application(bootcamp_data, completed_app_data):
    """
    migrate_application should create a new application for a user in a new bootcamp run and
    copy over data from an existing application.
    """
    to_run = bootcamp_data.runs[1]
    to_run_application = migrate_application(
        from_run_application=completed_app_data.application, to_run=to_run
    )
    assert completed_app_data.application.state == AppStates.COMPLETE.value
    assert to_run_application.state == AppStates.AWAITING_PAYMENT.value
    assert to_run_application.user == completed_app_data.application.user
    assert to_run_application.bootcamp_run == to_run
    assert (
        to_run_application.resume_file.name
        == completed_app_data.application.resume_file.name
    )
    assert to_run_application.linkedin_url == FAKE_LINKEDIN_URL
    for i, submission in enumerate(to_run_application.submissions.all()):
        assert submission.review_status == REVIEW_STATUS_APPROVED
        assert submission.run_application_step in bootcamp_data.run_app_steps[to_run.id]
        assert submission.object_id == completed_app_data.submissions[i].object_id


@pytest.mark.django_db
def test_migrate_application_different_order(bootcamp_data, completed_app_data):
    """
    migrate_application should be able to migrate an application between runs of two different bootcamps, even if the
    application steps are in a different order.
    """
    new_bootcamp_run = BootcampRunFactory.create()
    InstallmentFactory.create(amount=BOOTCAMP_PRICE, bootcamp_run=new_bootcamp_run)
    new_app_steps = ApplicationStepFactory.create_batch(
        len(bootcamp_data.app_steps),
        bootcamp=new_bootcamp_run.bootcamp,
        # Use the same application steps as the existing bootcamp, but in reverse order
        submission_type=factory.Iterator(reversed(bootcamp_data.submission_types)),
        step_order=factory.Iterator([1, 2, 3]),
    )
    run_app_steps = BootcampRunApplicationStepFactory.create_batch(
        len(new_app_steps),
        bootcamp_run=new_bootcamp_run,
        application_step=factory.Iterator(new_app_steps),
    )

    new_run_application = migrate_application(
        from_run_application=completed_app_data.application, to_run=new_bootcamp_run
    )
    assert new_run_application.state == AppStates.AWAITING_PAYMENT.value
    ordered_submissions = list(
        new_run_application.submissions.order_by(
            "run_application_step__application_step__step_order"
        )
    )
    for i, submission in enumerate(ordered_submissions):
        assert submission.review_status == REVIEW_STATUS_APPROVED
        assert submission.run_application_step == run_app_steps[i]
    # The submissions for the new application should be copied over for the existing one, but the application steps
    # are in a different order.
    assert [sub.object_id for sub in ordered_submissions] == [
        completed_app_data.submissions[2].object_id,
        completed_app_data.submissions[0].object_id,
        completed_app_data.submissions[1].object_id,
    ]


@pytest.mark.django_db
def test_migrate_application_existing(bootcamp_data, completed_app_data):
    """
    migrate_application should raise an exception if there is already an application in an approved
    state for the 'to' run.
    """
    to_run = bootcamp_data.runs[1]
    BootcampApplicationFactory.create(
        bootcamp_run=to_run,
        user=completed_app_data.application.user,
        state=AppStates.COMPLETE,
    )
    with pytest.raises(ValidationError):
        migrate_application(
            from_run_application=completed_app_data.application, to_run=to_run
        )


@pytest.mark.django_db
def test_has_same_application_steps(bootcamp_data):
    """
    has_same_application_steps should return True if the two bootcamp ids refer to a
    set of equivalent application steps
    """
    existing_bootcamp = bootcamp_data.runs[0].bootcamp
    assert (
        has_same_application_steps(existing_bootcamp.id, existing_bootcamp.id) is True
    )
    new_bootcamp = BootcampFactory.create()
    existing_bootcamp_steps = list(bootcamp_data.app_steps)
    ApplicationStepFactory.create_batch(
        len(bootcamp_data.app_steps),
        bootcamp=new_bootcamp,
        submission_type=factory.Iterator(
            [step.submission_type for step in existing_bootcamp_steps]
        ),
        step_order=factory.Iterator(
            [step.step_order for step in existing_bootcamp_steps]
        ),
    )
    assert has_same_application_steps(existing_bootcamp.id, new_bootcamp.id) is True
    # If a step is removed/added/updated, this function should return False
    step = new_bootcamp.application_steps.first()
    step.delete()
    assert has_same_application_steps(existing_bootcamp.id, new_bootcamp.id) is False


@pytest.mark.django_db
def test_has_same_application_steps_order():
    """
    has_same_application_steps should take a flag that determines whether it will return True if the bootcamps
    have the same steps in a different order.
    """
    submission_types = [SUBMISSION_VIDEO, SUBMISSION_QUIZ]
    bootcamps = BootcampFactory.create_batch(2)
    ApplicationStepFactory.create_batch(
        len(submission_types),
        bootcamp=bootcamps[0],
        submission_type=factory.Iterator(submission_types),
        step_order=factory.Iterator([1, 2]),
    )
    ApplicationStepFactory.create_batch(
        len(submission_types),
        bootcamp=bootcamps[1],
        submission_type=factory.Iterator(reversed(submission_types)),
        step_order=factory.Iterator([1, 2]),
    )
    assert (
        has_same_application_steps(bootcamps[0].id, bootcamps[1].id, ignore_order=True)
        is True
    )
    assert (
        has_same_application_steps(bootcamps[0].id, bootcamps[1].id, ignore_order=False)
        is False
    )
