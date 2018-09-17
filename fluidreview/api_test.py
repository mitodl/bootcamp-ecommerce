"""
FluidReview Backend Tests
"""
import datetime
import json
from decimal import Decimal

from unittest.mock import patch
import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from requests import HTTPError

from ecommerce.factories import OrderFactory, LineFactory
from ecommerce.models import Order
from fluidreview.constants import WebhookParseStatus
from fluidreview.factories import OAuthTokenFactory, WebhookRequestFactory
from fluidreview.api import FluidReviewAPI, BASE_API_URL, process_user, parse_webhook, list_users, post_payment, \
    FluidReviewException
from fluidreview.models import OAuthToken, WebhookRequest
from fluidreview.utils import utc_now
from klasses.factories import KlassFactory, InstallmentFactory
from klasses.models import Bootcamp, Klass, PersonalPrice
from profiles.factories import UserFactory, ProfileFactory
from profiles.models import Profile

pytestmark = pytest.mark.django_db

# pylint: disable=redefined-outer-name

fluid_user = {
    'id': 21231,
    'email': 'fluid_user@fluid.xyz',
    'full_name': 'Fluid User'
}


@pytest.fixture()
def test_payment_data():
    """
    Sets up the data for payment tests in this module
    """
    klass = KlassFactory()
    profile = ProfileFactory(fluidreview_id=1)
    InstallmentFactory(klass=klass)
    order = OrderFactory(user=profile.user, status=Order.FULFILLED)
    LineFactory.create(order=order, klass_key=klass.klass_key, price=11.38)
    webhook = WebhookRequestFactory(
        award_id=klass.klass_key, status=WebhookParseStatus.SUCCEEDED, user_id=profile.fluidreview_id, submission_id=1
    )

    return klass, order, webhook


def test_get_token_from_settings(settings):
    """ Test that the FluidReviewAPI instance token is initially based off settings"""
    settings.FLUIDREVIEW_ACCESS_TOKEN = 'fakeaccesstoken'
    settings.FLUIDREVIEW_REFRESH_TOKEN = 'fakerefreshtoken'
    frapi = FluidReviewAPI()
    token = frapi.get_token()
    assert token['access_token'] == settings.FLUIDREVIEW_ACCESS_TOKEN
    assert token['refresh_token'] == settings.FLUIDREVIEW_REFRESH_TOKEN


def test_get_token_from_database():
    """ Test that a FluidReviewAPI instance token is retrieved from the database if it exists"""
    dbtoken = OAuthTokenFactory(expires_on=utc_now())
    frapi = FluidReviewAPI()
    token = frapi.get_token()
    assert token['access_token'] == dbtoken.access_token
    assert token['refresh_token'] == dbtoken.refresh_token


def test_save_token_new():
    """Test that the save_token method correctly creates a new OAuthToken in the database"""
    assert OAuthToken.objects.first() is None
    response_token = {
        'access_token': 'fakeaccesstoken',
        'refresh_token': 'fakerefreshtoken',
        'expires_in': 1000,
        'token_type': 'faketype'
    }
    frapi = FluidReviewAPI()
    now = utc_now()
    new_token = frapi.save_token(response_token)
    for attr in ['access_token', 'refresh_token', 'token_type']:
        assert response_token[attr] == getattr(new_token, attr)
        assert response_token[attr] == new_token.json[attr]
    # Ensure expires_on, expires_in values are close to expected value
    assert now + datetime.timedelta(seconds=985) <= new_token.expires_on <= now + datetime.timedelta(seconds=1000)
    assert 985 <= new_token.json['expires_in'] < 1000


def test_save_token_update():
    """Test that the save_token method correctly updates an existing OAuthToken in the database"""
    initial_token = OAuthTokenFactory(
        expires_on=utc_now() - datetime.timedelta(seconds=7200),
        access_token='oldaccess',
        refresh_token='oldrefresh'
    )
    response_token = {
        'access_token': 'fakeaccesstoken',
        'refresh_token': 'fakerefreshtoken',
        'expires_in': 7200,
        'token_type': 'faketype'
    }
    base_attrs = ['access_token', 'refresh_token', 'token_type']
    frapi = FluidReviewAPI()
    for attr in base_attrs:
        assert getattr(initial_token, attr) == frapi.session.token[attr]
    frapi.save_token(response_token)
    frapi.session = frapi.initialize_session()
    for attr in base_attrs:
        assert response_token[attr] == frapi.session.token[attr]
    # Ensure expires_in is close to expected value
    assert 7185 <= frapi.session.token['expires_in'] <= 7200


@override_settings(FLUIDREVIEW_BASE_URL="http://test.bootcamp.zzz")
@pytest.mark.parametrize(['method', 'url', 'full_url', 'kwargs'], [
    ['get', 'users', '{}users', {}],
    ['get', '/users', '{}users', {}],
    ['get', '/users?testing=true', '{}users?testing=true', {}],
    ['put', 'installments/2', '{}installments/2', {'data': {'transaction': 1}}],
    ['post', 'transactions', '{}transactions', {'data': {'application': 3}}]
])
def test_oauth_requests(mocker, method, url, full_url, kwargs):
    """Test that OAuth2Session calls the correct request method with correct arguments"""
    mock_oauth = mocker.patch('fluidreview.api.OAuth2Session.{}'.format(method))
    FluidReviewAPI().request(method, url, **kwargs)
    mock_oauth.assert_called_once_with(full_url.format(BASE_API_URL), **kwargs)


@pytest.mark.parametrize(['method', 'url', 'kwargs'], [
    ['get', 'users', {}],
    ['put', 'installments/2', {'data': {'transaction': 1}}],
    ['post', 'transactions', {'data': {'application': 3}}]
])
def test_api_requests(mocker, method, url, kwargs):
    """Test that FluidReviewAPI.request method gets called with the correct arguments"""
    mock_request = mocker.patch('fluidreview.api.FluidReviewAPI.request')
    frapi = FluidReviewAPI()
    getattr(frapi, method)(url, **kwargs)
    mock_request.assert_called_once_with(method, url, **kwargs)


def test_api_request_invalid_token(mocker):
    """Test that a request will be tried 2x and the session reinitialized if the tokens are no longer valid"""
    mock_session = mocker.patch('fluidreview.api.OAuth2Session')
    mock_init = mocker.patch('fluidreview.api.FluidReviewAPI.initialize_session', return_value=mock_session)
    mock_session.get.return_value.status_code = 401
    frapi = FluidReviewAPI()
    frapi.get('users')
    assert mock_session.get.call_count == 2
    assert mock_init.call_count == 2


def test_process_new_user():
    """Test that a new user and profile are successfully created"""
    assert User.objects.filter(email=fluid_user['email']).first() is None
    assert Profile.objects.filter(fluidreview_id=fluid_user['id']).first() is None
    process_user(fluid_user)
    assert User.objects.filter(email=fluid_user['email']).count() == 1
    new_profile = Profile.objects.get(fluidreview_id=fluid_user["id"])
    assert new_profile.name == fluid_user['full_name']
    assert new_profile.user.email == fluid_user['email']


def test_process_new_profile():
    """Test that a new profile is successfully created for an existing user"""
    UserFactory(email=fluid_user['email'], username='fluid_user')
    assert User.objects.filter(email=fluid_user['email']).first().username == 'fluid_user'
    assert Profile.objects.filter(fluidreview_id=fluid_user['id']).first() is None
    process_user(fluid_user)
    assert User.objects.filter(email=fluid_user['email']).count() == 1
    assert Profile.objects.filter(fluidreview_id=fluid_user['id']).count() == 1


def test_process_both_exist_no_fluid_id(mocker):
    """Test that no changes are made to an existing user but existing profile is saved with fluid id"""
    ProfileFactory(
        user=UserFactory(email=fluid_user['email'].upper(), username=fluid_user['email']),
        fluidreview_id=None
    )
    mock_create_user = mocker.patch('fluidreview.api.User.objects.create')
    process_user(fluid_user)
    mock_create_user.assert_not_called()
    assert Profile.objects.filter(fluidreview_id=fluid_user['id']).count() == 1


def test_process_user_both_exist_with_fluid_id(mocker):
    """Test that no changes are made to an existing user and profile with fluidreview id"""
    ProfileFactory(
        user=UserFactory(email=fluid_user['email'].upper(), username=fluid_user['email']),
        fluidreview_id=1
    )
    mock_create_user = mocker.patch('fluidreview.api.User.objects.create')
    mock_save_profile = mocker.patch('fluidreview.api.Profile.save')
    process_user(fluid_user)
    mock_create_user.assert_not_called()
    mock_save_profile.assert_not_called()


@pytest.mark.parametrize(['amount_to_pay', 'award_cost', 'sends_email'], [
    ['', '1000.10', False],
    ['25.99', '', False],
    ['', '', True]
])
def test_parse_webhook_user(mocker, amount_to_pay, award_cost, sends_email):
    """Test creation of new Bootcamp if no matching award_id"""
    user_id = 94379385
    award_id = 78456
    award_name = "Best monkey prize"
    ProfileFactory(fluidreview_id=user_id)
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().get.return_value.json.return_value = {
        'id': award_id,
        'name': award_name,
        'tag_line': 'The very best!',
        'description': '',
        'amount_to_pay': '450',
    }
    data = {
        'date_of_birth': '',
        'user_email': 'veteran-grants-9463shC',
        'amount_to_pay': amount_to_pay,
        'user_id': user_id,
        'submission_id': 4533767,
        'award_id': award_id,
        'award_cost': award_cost,
        'award_name': 'TEST CAMP'
    }
    body = json.dumps(data)
    hook = WebhookRequest(body=body)

    with patch(
        'fluidreview.api.MailgunClient.send_individual_email',
    ) as send_email:
        if sends_email:
            assert send_email.call_count == 0
        else:
            parse_webhook(hook)
            assert Klass.objects.filter(klass_key=award_id).exists()
            assert Bootcamp.objects.filter(title=award_name).exists()
            assert PersonalPrice.objects.filter(
                klass__klass_key=award_id,
                user__profile__fluidreview_id=user_id
            ).exists()
            assert send_email.call_count == 1
            assert send_email.call_args[0] == (
                "Klass and Bootcamp created, for klass_key {klass_key}".format(klass_key=award_id),
                "Klass and Bootcamp created, for klass_key {klass_key}".format(klass_key=award_id),
                'support@example.com',
            )


@pytest.mark.parametrize('award_id', [81265, None])
@pytest.mark.parametrize(['amount_to_pay', 'award_cost', 'user_price'], [
    ['', '1000.10', '1000.10'],
    ['25.99', '', '25.99'],
    ['', '', None],
    ['0', '400', '0'],
    ['10', '400', '10']
])
def test_parse_success(mocker, amount_to_pay, award_cost, user_price, award_id):
    """Test that a webhookrequest body is successfully parsed into individual fields"""
    klass = KlassFactory.create(klass_key=81265)
    user_id = 94379385
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().get.return_value.json.return_value = {
        'id': 94379385,
        'full_name': 'Veteran Grants 9463shC',
        'email': 'veteran-grants-9463shC'
    }
    data = {
        'date_of_birth': '',
        'user_email': 'veteran-grants-9463shC',
        'amount_to_pay': amount_to_pay,
        'user_id': user_id,
        'submission_id': 4533767,
        'award_id': award_id,
        'award_cost': award_cost,
        'award_name': 'TEST CAMP'
    }
    body = json.dumps(data)
    hook = WebhookRequest(body=body)
    parse_webhook(hook)
    for attr in ('user_email', 'user_id', 'submission_id', 'award_id', 'award_name'):
        assert getattr(hook, attr) == data[attr]
    assert hook.amount_to_pay == (Decimal(data['amount_to_pay']) if amount_to_pay != '' else None)
    assert hook.award_cost == (Decimal(data['award_cost']) if award_cost != '' else None)
    assert hook.status == WebhookParseStatus.SUCCEEDED
    if award_id is not None and user_price is not None:
        assert klass.personal_price(User.objects.get(profile__fluidreview_id=user_id)) == Decimal(user_price)
    else:
        assert klass.personal_price(User.objects.get(profile__fluidreview_id=user_id)) == klass.price


@pytest.mark.parametrize('body', [
    '',
    'hello world',
    '{"user_email": "foo@bar.com", "user_id": 94379385, "award_id": 1, "award_cost": "BADVALUE", "submission_id": 1}',
    '{"user_email": "foo@bar.com", "user_id": "", "award_id": 1, "award_cost": "100", "submission_id": 1}',
    '{"user_email": "foo@bar.com", "user_id": null, "award_id": 1, "award_cost": "100", "submission_id": 1}',
    '{"user_email": "foo@bar.com", "user_id": 94379385, "award_id": "a", "award_cost": "", "submission_id": 1}',
    '{"user_email": "foo@bar.com", "user_id": 94379385, "award_id": 1, "award_cost": 1, "submission_id": 1}',
])
def test_parse_failure(mocker, body):
    """Test that a webhookrequest's status is set to FAILED if it cannot be parsed"""
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().get.return_value.json.return_value = {
        'id': 94379385,
        'full_name': 'Veteran Grants 9463shC',
        'email': 'veteran-grants-9463shC'
    }
    request = WebhookRequest(body=body)
    parse_webhook(request)
    assert request.status == WebhookParseStatus.FAILED


def test_list_users(mocker):
    """
    Test that the list_users method yields expected results
    """
    mock_api_results = [
        {
            'count': 3,
            'next': 'https://bootcampmit.fluidreview.com/api/v2/users/?page=2',
            'previous': None,
            'results': [
                {
                    'email': 'fake1@edu.mit',
                    'id': 94379401
                },
                {
                    'email': 'fake2@edu.mit',
                    'id': 94379359,
                }
            ]
        },
        {
            'count': 3,
            'next': None,
            'previous': 'https://bootcampmit.fluidreview.com/api/v2/users',
            'results': [
                {
                    'email': 'fake3@edu.mit',
                    'id': 94379422
                }
            ]
        },
    ]
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().get.return_value.json.side_effect = mock_api_results
    expected_users = [user for results in mock_api_results for user in results['results']]
    assert expected_users == [user for user in list_users()]


@pytest.mark.parametrize('is_legacy', [True, False])
@pytest.mark.parametrize('is_fulfilled', [True, False])
def test_post_payment(mocker, is_legacy, is_fulfilled, test_payment_data, settings):
    """Test that posting a payment is called for non-legacy klasses, with correct data"""
    settings.FLUIDREVIEW_AMOUNTPAID_ID = 100
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().put.return_value.status_code = 200
    klass, order, hook = test_payment_data
    if not is_fulfilled:
        order.status = Order.FAILED
    Bootcamp.objects.filter(id=klass.bootcamp.id).update(legacy=is_legacy)
    post_payment(order)
    expected_data = {'value': '11.38'}
    assert mock_api().put.call_count == (0 if is_legacy or not is_fulfilled else 1)
    if is_fulfilled and not is_legacy:
        mock_api().put.assert_called_with(
            'submissions/{}/metadata/100/'.format(hook.submission_id), data=expected_data
        )


def test_post_payment_bad_response(mocker, test_payment_data):
    """Test that bad responses from FluidReview raise expected exceptions"""
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().put.side_effect = HTTPError
    klass, order, _ = test_payment_data
    Bootcamp.objects.filter(id=klass.bootcamp.id).update(legacy=False)
    with pytest.raises(FluidReviewException) as exc:
        post_payment(order)
    assert 'Error updating amount paid by user' in str(exc)


def test_post_payment_bad_webhook(mocker, test_payment_data):
    """Test that a webhook without submission id raises expected exception"""
    mocker.patch('fluidreview.api.FluidReviewAPI')
    klass, order, hook = test_payment_data
    hook.submission_id = None
    hook.save()
    Bootcamp.objects.filter(id=klass.bootcamp.id).update(legacy=False)
    with pytest.raises(FluidReviewException) as exc:
        post_payment(order)
    assert 'Webhook has no submission id for order' in str(exc)
