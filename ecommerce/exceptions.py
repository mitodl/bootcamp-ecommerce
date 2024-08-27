"""
Exceptions for ecommerce
"""


class EcommerceException(Exception):  # noqa: N818
    """
    General exception regarding ecommerce
    """


class EcommerceModelException(Exception):  # noqa: N818
    """
    Exception regarding ecommerce models
    """


class ParseException(Exception):  # noqa: N818
    """
    Exception regarding parsing CyberSource reference numbers
    """


class WireTransferImportException(Exception):  # noqa: N818
    """
    Exception regarding importing wire transfer CSV files
    """
