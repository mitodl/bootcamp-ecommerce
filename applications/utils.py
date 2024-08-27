"""
Application utils
"""

import os

from django.core.exceptions import ValidationError


def validate_file_extension(value):
    """
    Check the file extension is allowed

    Args:
        value (File): file name
    """
    ext = os.path.splitext(value.name)[1]  # noqa: PTH122
    valid_extensions = [".pdf", ".doc", ".docx", ".odt"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Unsupported file extension.")  # noqa: EM101


def check_eligibility_to_skip_steps(bootcamp_application):
    """
    Check the eligibility to skip the application steps of

    Args:
        bootcamp_application (BootcampApplication)
    """
    return (
        bootcamp_application.user.profile.can_skip_application_steps
        and bootcamp_application.bootcamp_run.allows_skipped_steps
    )
