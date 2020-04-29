"""
APIs to access the remote bootcamp app that controls the admissions
"""
import logging

from fluidreview.constants import WebhookParseStatus
from fluidreview.models import WebhookRequest
from smapply.models import WebhookRequestSMA

log = logging.getLogger(__name__)


def fetch_fluidreview_klass_keys(fluid_user_id):
    """
    Collect all the unique award ids (== klass ids) from WebhookRequests by user email

    Args:
        fluid_user_id(int): FluidReview id for a user

    Returns:
        list: FluidReview award_ids for a user
    """
    return list(
        WebhookRequest.objects.filter(
            user_id=fluid_user_id,
            status=WebhookParseStatus.SUCCEEDED
        ).distinct('award_id').values_list('award_id', flat=True)
    )


def fetch_smapply_klass_keys(sma_user_id):
    """
    Collect all the unique award ids (== klass ids) from WebhookRequestSMA by user email

    Args:
        sma_user_id(int): SMApply id for a user

    Returns:
        list: SMApply award_ids for a user
    """
    return list(
        WebhookRequestSMA.objects.filter(
            user_id=sma_user_id,
            status=WebhookParseStatus.SUCCEEDED
        ).distinct('award_id').values_list('award_id', flat=True)
    )


class BootcampAdmissionClient:
    """
    Client for the retrieving information about user admissions to klasses
    """

    def __init__(self, user):
        """
        Fetch information about a user's admissions for the bootcamp

        Args:
            user (User): A user
        """
        self._klass_keys = fetch_fluidreview_klass_keys(user.profile.fluidreview_id) + \
            fetch_smapply_klass_keys(user.profile.smapply_id) + [12345]

    @property
    def payable_klasses_keys(self):
        """
        A list of klass keys which the user can pay for
        """
        return self._klass_keys

    def can_pay_klass(self, klass_key):
        """
        Whether the user can pay for a specific klass
        """
        return klass_key in self.payable_klasses_keys
