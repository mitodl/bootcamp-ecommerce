"""
API functionality for bootcamps
"""
from klasses.models import BootcampRun


def deactivate_run_enrollment(run_enrollment, change_status):
    """
    Helper method to deactivate a BootcampRunEnrollment

    Args:
        run_enrollment (BootcampRunEnrollment): The bootcamp run enrollment to deactivate
        change_status (str): The change status to set on the enrollment when deactivating

    Returns:
        BootcampRunEnrollment: The updated enrollment
    """
    run_enrollment.active = False
    run_enrollment.change_status = change_status
    run_enrollment.save()


def fetch_bootcamp_run(run_property):
    """
    Fetches a bootcamp run that has a field value (id, title, etc.) that matches the given property

    Args:
        run_property (str): A string representing some field value for a specific bootcamp run

    Returns:
        BootcampRun: The bootcamp run matching the given property
    """
    if run_property.isdigit():
        return BootcampRun.objects.get(id=run_property)
    return BootcampRun.objects.get(title=run_property)
