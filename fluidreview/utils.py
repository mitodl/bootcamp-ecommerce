""" Utility functions for fluidreview """
from datetime import datetime
import pytz


def utc_now():
    """
    Get the current date/time

    Returns:
        datetime: Current date/time

    """
    return datetime.now(tz=pytz.UTC)
