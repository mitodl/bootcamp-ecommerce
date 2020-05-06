"""
APIs for the bootcamps app
"""
from decimal import Decimal

from ecommerce.models import Line
from ecommerce.serializers import LineSerializer
from klasses.bootcamp_admissions_client import BootcampAdmissionClient
from klasses.models import BootcampRun
from klasses.serializers import InstallmentSerializer


def serialize_user_bootcamp_runs(user):
    """
    Returns serialized bootcamp run and payment details for a user.
    Note, this function will combine the bootcamp runs for orders already placed and
    the bootcamp runs from the remote authorization system.

    This is to prevent that a failure of the remote system will prevent the user to
    see the payments already done. In this case, though, the user will not be authorized to make additional
    payments but just to see the ones already made.

    Args:
        user (User): a user

    Returns:
        list: list of dictionaries describing a bootcamp run and payments for it by the user
    """
    # extract the payments already done.
    run_keys_in_lines = list(Line.fulfilled_for_user(user).values_list(
        'run_key', flat=True).distinct())

    bootcamp_client = BootcampAdmissionClient(user)
    all_bootcamp_run_keys = list(set(run_keys_in_lines).union(set(bootcamp_client.payable_bootcamp_run_keys)))
    bootcamp_runs_qset = (
        BootcampRun.objects.filter(run_key__in=all_bootcamp_run_keys)
        .select_related('bootcamp').order_by('run_key')
    )

    return [serialize_user_bootcamp_run(user, bootcamp_run, bootcamp_client) for bootcamp_run in bootcamp_runs_qset]


def serialize_user_bootcamp_run(user, bootcamp_run, bootcamp_client=None):
    """
    Returns the bootcamp run info for the user with payments details.

    Args:
        user (User): a user
        bootcamp_run (klasses.models.BootcampRun): a bootcamp run
        bootcamp_client (BootcampAdmissionClient): an instance of the client to retrieve data
            from the bootcamp authorization system

    Returns:
        dict: a dictionary describing a bootcamp run and payments for it by the user
    """
    if bootcamp_client is None:
        bootcamp_client = BootcampAdmissionClient(user)

    return {
        "run_key": bootcamp_run.run_key,
        "bootcamp_run_name": bootcamp_run.title,
        "display_title": bootcamp_run.display_title,
        "start_date": bootcamp_run.start_date,
        "end_date": bootcamp_run.end_date,
        "price": bootcamp_run.personal_price(user),
        "is_user_eligible_to_pay": bootcamp_client.can_pay_bootcamp_run(bootcamp_run.run_key),
        "total_paid": Line.total_paid_for_bootcamp_run(user, bootcamp_run.run_key).get('total') or Decimal('0.00'),
        "payments": LineSerializer(Line.for_user_bootcamp_run(user, bootcamp_run.run_key), many=True).data,
        "installments": InstallmentSerializer(bootcamp_run.installment_set.order_by('deadline'), many=True).data,
    }
