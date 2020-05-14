"""
APIs for the bootcamps app
"""
from django.db.models import Q

from applications.constants import AppStates
from klasses.models import BootcampRun


def payable_bootcamp_run_keys(user):
    """
    Fetches a list of bootcamp run keys for which the user has applied

    Args:
        user (User): a user

    Returns:
        list of int: bootcamp run keys the user has applied for

    """
    return (
        BootcampRun.objects.prefetch_related("applications")
            .filter((Q(applications__user=user) & Q(applications__state=AppStates.AWAITING_PAYMENT.value)) |
                    Q(personal_prices__user=user))
            .values_list("run_key", flat=True)
    )
