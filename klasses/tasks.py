"""
Tasks for the klass app
"""
import logging

from django.contrib.auth.models import User

from bootcamp.celery import async
from klasses.models import Klass, BootcampAdmissionCache

log = logging.getLogger(__name__)


def _cache_admissions(user_email, payable_klasses):
    """
    Caches the admissions for which the user is allowed to pay.

    Args:
        user_email (str): the email corresponding to an User
        payable_klasses (list): a list built by BootcampAdmissionClient._get_payable_klasses
    """
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        log.exception('User with email %s does not exists', user_email)
        return

    payable_klasses_lookup = {klass['klass_id']: klass for klass in payable_klasses}
    payable_klasses_keys = list(payable_klasses_lookup.keys())
    local_klasses = Klass.objects.filter(klass_key__in=payable_klasses_keys)

    for klass in local_klasses:
        updated_values = {
            'user': user,
            'klass': klass,
            'data': payable_klasses_lookup[klass.klass_key],
        }
        BootcampAdmissionCache.objects.update_or_create(
            user=user,
            klass=klass,
            defaults=updated_values
        )
    # delete anything is not in the current admissions
    BootcampAdmissionCache.delete_all_but(user, payable_klasses_keys)


@async.task
def async_cache_admissions(user_email, payable_klasses):
    """
    Takes care of calling the function to cache the admissions for which the user is allowed to pay.

    Args:
        user_email (str): the email corresponding to an User
        payable_klasses (list): a list built by BootcampAdmissionClient._get_payable_klasses
    """
    _cache_admissions(user_email, payable_klasses)
