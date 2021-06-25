"""Utility functions/classes for bootcamp management commands"""
from django.core.management.base import BaseCommand

from mitol.common.utils import has_equal_properties


def enrollment_summary(enrollment):
    """
    Returns a string representation of an enrollment for command output

    Args:
        enrollment (BootcampRunEnrollment): The enrollment
    Returns:
        str: A string representation of an enrollment
    """
    return "<BootcampRunEnrollment: id={}, run={}>".format(
        enrollment.id, enrollment.bootcamp_run.bootcamp_run_id
    )


def enrollment_summaries(enrollments):
    """
    Returns a list of string representations of enrollments for command output

    Args:
        enrollments (iterable of BootcamRunEnrollment): The enrollments
    Returns:
        list of str: A list of string representations of enrollments
    """
    return list(map(enrollment_summary, enrollments))


def create_or_update_enrollment(model_cls, defaults=None, **kwargs):
    """Creates or updates an enrollment record"""
    defaults = {**(defaults or {}), "active": True, "change_status": None}
    created = False
    enrollment = model_cls.all_objects.filter(**kwargs).order_by("-created_on").first()
    if not enrollment:
        enrollment = model_cls.objects.create(**{**defaults, **kwargs})
        created = True
    elif enrollment and not has_equal_properties(enrollment, defaults):
        for field_name, field_value in defaults.items():
            setattr(enrollment, field_name, field_value)
        enrollment.save_and_log(None)
    return enrollment, created


class EnrollmentChangeCommand(BaseCommand):
    """Base class for management commands that change enrollment status"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            dest="force",
            help="Ignores validation when performing the desired status change",
        )

    def handle(self, *args, **options):
        pass
