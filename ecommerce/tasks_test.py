"""Ecommerce task tests"""
from ecommerce.tasks import send_receipt_email


def test_send_receipt_email(mocker):
    """Test send_receipt_email"""
    mock_api = mocker.patch("ecommerce.tasks.api")
    send_receipt_email.delay(123)
    mock_api.send_receipt_email.assert_called_once_with(123)
