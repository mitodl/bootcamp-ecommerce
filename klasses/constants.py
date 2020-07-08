"""Klasses constants"""


class ApplicationSource:
    """Simple class for possible WebHookRequest parsing statuses"""

    SMAPPLY = "SMApply"
    FLUIDREVIEW = "FluidRev"

    SOURCE_CHOICES = [None, SMAPPLY, FLUIDREVIEW]


INTEGRATION_PREFIX_PRODUCT = "BootcampProduct-"

ENROLL_CHANGE_STATUS_REFUNDED = "refunded"
ALL_ENROLL_CHANGE_STATUSES = [
    # Deferral may be added layer, just refunds for now
    ENROLL_CHANGE_STATUS_REFUNDED
]
ENROLL_CHANGE_STATUS_CHOICES = list(
    zip(ALL_ENROLL_CHANGE_STATUSES, ALL_ENROLL_CHANGE_STATUSES)
)
