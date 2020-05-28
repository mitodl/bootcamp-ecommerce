"""
Decorators for hubspot module
"""
import functools
from time import sleep

from requests import HTTPError


def try_again(func):
    """
    Wrapper for sending requests to hubspot. Attempts to send requests multiple times.
    Hubspot does not seem to return 429 errors so any error is considered a too many requests error for the purposes
    of try again.

    The wrapped function should return a requests response object.
    """

    @functools.wraps(func)
    def wrapper_try_again(*args, **kwargs):
        max_attempts = 3
        for i in range(max_attempts):
            resp = func(*args, **kwargs)
            try:
                # If response does not raise an error, return it
                resp.raise_for_status()
                return resp
            except HTTPError:
                if i + 1 == max_attempts:
                    # If we have already tried three times, return response and let the code handle it as normal
                    return resp
                # Wait 2 seconds in between attempts
                sleep(2)

    return wrapper_try_again
