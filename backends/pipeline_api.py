"""
APIs for extending the python social auth pipeline
"""
import logging
from datetime import datetime

import pytz


log = logging.getLogger(__name__)


def set_last_update(details, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Pipeline function to add extra information about when the social auth
    profile has been updated.

    Args:
        details (dict): dictionary of informations about the user

    Returns:
        dict: updated details dictionary
    """
    details['updated_at'] = datetime.now(tz=pytz.UTC).timestamp()
    return details
