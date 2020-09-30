"""
Exceptions for ecommerce
"""


class EcommerceException(Exception):
    """
    General exception regarding ecommerce
    """


class EcommerceModelException(Exception):
    """
    Exception regarding ecommerce models
    """


class ParseException(Exception):
    """
    Exception regarding parsing CyberSource reference numbers
    """


class WireTransferImportException(Exception):
    """
    Exception regarding importing wire transfer CSV files
    """
