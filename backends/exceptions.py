"""
Exceptions for backends app
"""


class InvalidCredentialStored(Exception):  # noqa: N818
    """Custom exception to throw in some specific situations"""

    def __init__(self, message, http_status_code):
        super(InvalidCredentialStored, self).__init__(message)  # noqa: UP008
        self.http_status_code = http_status_code
