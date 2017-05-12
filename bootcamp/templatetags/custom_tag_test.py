"""
Tests for custom template tags
"""
from datetime import datetime
from pytz import utc
from bootcamp.templatetags.dollar_format import dollar_format
from bootcamp.templatetags.parse_date import parse_iso_datetime


def test_dollar_format():
    """Test that dollar_format takes a number representing a dollar value and formats it correctly"""
    assert dollar_format('123') == '$123.00'
    assert dollar_format('123.5') == '$123.50'
    assert dollar_format(123) == '$123.00'
    assert dollar_format(123.5) == '$123.50'


def test_parse_iso_datetime():
    """Test that parse_iso_datetime correctly formats an ISO 8601 date string"""
    parsed_datetime = parse_iso_datetime('2017-01-01T01:01:01.000000Z')
    assert parsed_datetime == datetime(year=2017, month=1, day=1, hour=1, minute=1, second=1, tzinfo=utc)
    assert parse_iso_datetime('invalid') is None
