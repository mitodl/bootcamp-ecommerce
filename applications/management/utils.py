"""Application management command utility functions"""

from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import transaction

from applications.api import derive_application_state
from applications.constants import APPROVED_APP_STATES
from applications.models import (
    BootcampApplication,
    ApplicationStepSubmission,
    ApplicationStep,
)
from klasses.models import BootcampRun
from main.utils import is_empty_file


def fetch_bootcamp_run(run_property):
    """
    Fetches a bootcamp run based on a given property, which could refer to a few different fields

    Args:
        run_property (str): A string indicating an id, title, etc.

    Returns:
         BootcampRun: The bootcamp run that matches the given property
    """
    if run_property.isdigit():
        bootcamp_run = BootcampRun.objects.get(id=run_property)
    else:
        bootcamp_run = BootcampRun.objects.get(title=run_property)
    return bootcamp_run


def has_same_application_steps(bootcamp_id1, bootcamp_id2, ignore_order=True):
    """
    Returns True if the application steps are the same for the bootcamps indicated by the given ids

    Args:
        bootcamp_id1 (int): A bootcamp id
        bootcamp_id2 (int): Another bootcamp id
        ignore_order (bool): If set to True, the function will still return True if the two bootcamps have the same
            steps in a different order.

    Returns:
        bool: True if the application steps are the same for the bootcamps indicated by the given ids
    """
    if bootcamp_id1 == bootcamp_id2:
        return True
    first_bootcamp_app_steps = ApplicationStep.objects.filter(bootcamp_id=bootcamp_id1)
    second_bootcamp_app_steps = ApplicationStep.objects.filter(bootcamp_id=bootcamp_id2)
    order_by_field = "submission_type" if ignore_order else "step_order"
    first_bootcamp_step_types = list(
        first_bootcamp_app_steps.order_by(order_by_field).values_list(
            "submission_type", flat=True
        )
    )
    second_bootcamp_step_types = list(
        second_bootcamp_app_steps.order_by(order_by_field).values_list(
            "submission_type", flat=True
        )
    )
    return first_bootcamp_step_types == second_bootcamp_step_types


def migrate_application(from_run_application, to_run):
    """
    Given an existing application, creates a new application in a different bootcamp run and "migrates" over all of
    the data from the existing application. Assumes that the 'from' run and 'to' run have the same application steps.

    Args:
        from_run_application (BootcampApplication): The bootcamp application to copy
        to_run (BootcampRun): The bootcamp run for which a new application will be created

    Returns:
        BootcampApplication: The newly-created bootcamp application that was created based on the existing one.
    """
    has_completed_app = BootcampApplication.objects.filter(
        bootcamp_run=to_run,
        user=from_run_application.user,
        state__in=APPROVED_APP_STATES,
    ).exists()
    if has_completed_app:
        raise ValidationError(
            "An approved/completed application already exists for this user and run ({}, {})".format(
                from_run_application.user.email, to_run.title
            )
        )

    with transaction.atomic():
        (
            to_run_application,
            _,
        ) = BootcampApplication.objects.select_for_update().get_or_create(
            bootcamp_run=to_run, user=from_run_application.user
        )

        # Copy work history data
        if is_empty_file(to_run_application.resume_file) and not is_empty_file(
            from_run_application.resume_file
        ):
            to_run_application.resume_file.name = from_run_application.resume_file.name
        if (
            to_run_application.linkedin_url is None
            and from_run_application.linkedin_url is not None
        ):
            to_run_application.linkedin_url = from_run_application.linkedin_url
        to_run_application.resume_upload_date = from_run_application.resume_upload_date
        to_run_application.save()

        # Copy application submissions (video interview, etc.)
        from_app_step_submissions = ApplicationStepSubmission.objects.filter(
            bootcamp_application=from_run_application
        ).order_by("run_application_step__application_step__step_order")
        # Build a dict of each submission type mapped to a list of the bootcamp run application step ids that require
        # that submission type (e.g.: {"videointerviewsubmission": [1, 2], "quizsubmission": [3]}).
        to_run_step_qset = to_run.application_steps.order_by(
            "application_step__step_order"
        ).values("id", "application_step__submission_type")
        to_run_steps = defaultdict(list)
        for to_run_step in to_run_step_qset:
            submission_type = to_run_step["application_step__submission_type"]
            to_run_steps[submission_type].append(to_run_step["id"])
        # In order to make this work even if the 'from' and 'to' runs have possibly-repeated application steps in a
        # possibly-different order, keep track of the run step ids for which a submission has already been created.
        used_run_step_ids = set()
        for from_app_step_submission in from_app_step_submissions:
            submission_type = (
                from_app_step_submission.run_application_step.application_step.submission_type
            )
            to_run_step_id = next(
                step_id
                for step_id in to_run_steps[submission_type]
                if step_id not in used_run_step_ids
            )
            ApplicationStepSubmission.objects.update_or_create(
                bootcamp_application=to_run_application,
                run_application_step_id=to_run_step_id,
                defaults=dict(
                    review_status=from_app_step_submission.review_status,
                    review_status_date=from_app_step_submission.review_status_date,
                    submitted_date=from_app_step_submission.submitted_date,
                    submission_status=from_app_step_submission.submission_status,
                    content_type=from_app_step_submission.content_type,
                    object_id=from_app_step_submission.object_id,
                ),
            )
            used_run_step_ids.add(to_run_step_id)

        # Set state
        to_run_application.state = derive_application_state(to_run_application)
        to_run_application.save()
        return to_run_application
