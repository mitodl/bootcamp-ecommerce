"""
apis for the klasses app
"""
from decimal import Decimal

from ecommerce.models import Line
from ecommerce.serializers import LineSerializer
from klasses.bootcamp_admissions_client import BootcampAdmissionClient
from klasses.models import Klass
from klasses.serializers import InstallmentSerializer


def serialize_user_klasses(user):
    """
    Returns all klasses info for the user with payments details.
    Note, this function will combine the klasses for orders already placed and
    the klasses from the remote authorization system.

    This is to prevent that a failure of the remote system will prevent the user to
    see the payments already done. In this case, though, the user will not be authorized to make additional
    payments but just to see the ones already made.

    Args:
        user (User): a user

    Returns:
        list: list of dictionaries describing a klass and payments for it by the user
    """
    # extract the payments already done.
    klass_keys_in_lines = list(Line.fulfilled_for_user(user).values_list(
        'klass_key', flat=True).distinct())

    bootcamp_client = BootcampAdmissionClient(user)
    all_klasses_keys = list(set(klass_keys_in_lines).union(set(bootcamp_client.payable_klasses_keys)))
    klasses_qset = (
        Klass.objects.filter(klass_key__in=all_klasses_keys)
        .select_related('bootcamp').order_by('klass_key')
    )

    return [serialize_user_klass(user, klass, bootcamp_client) for klass in klasses_qset]


def serialize_user_klass(user, klass, bootcamp_client=None):
    """
    Returns the klass info for the user with payments details.

    Args:
        user (User): a user
        klass (klasses.models.Klass): a klass
        bootcamp_client (BootcampAdmissionClient): an instance of the client to retrieve informations
            from the bootcamp authorization system

    Returns:
        dict: a dictionary describing a klass and payments for it by the user
    """
    if bootcamp_client is None:
        bootcamp_client = BootcampAdmissionClient(user)

    return {
        "klass_key": klass.klass_key,
        "klass_name": klass.title,
        "display_title": klass.display_title,
        "start_date": klass.start_date,
        "end_date": klass.end_date,
        "price": klass.price,
        "is_user_eligible_to_pay": bootcamp_client.can_pay_klass(klass.klass_key),
        "total_paid": Line.total_paid_for_klass(user, klass.klass_key).get('total') or Decimal('0.00'),
        "payments": LineSerializer(Line.for_user_klass(user, klass.klass_key), many=True).data,
        "installments": InstallmentSerializer(klass.installment_set.order_by('deadline'), many=True).data,
    }
