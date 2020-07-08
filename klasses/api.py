"""
Functions for klasses
"""


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
