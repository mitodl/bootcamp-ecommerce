"""FluidReview constants"""


class WebhookParseStatus:
    """Simple class for possible WebHookRequest parsing statuses"""
    CREATED = 'Created'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'

    ALL_STATUSES = [
        CREATED,
        FAILED,
        SUCCEEDED
    ]
