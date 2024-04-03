"""Exceptions for applications"""

from rest_framework.exceptions import APIException


class InvalidApplicationStateException(APIException):
    """
    Custom exception for BootcampApplication
    """

    status_code = 409
    default_detail = "Bootcamp application is in invalid state"
    default_code = "invalid_application_state"
