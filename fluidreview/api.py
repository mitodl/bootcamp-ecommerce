"""
FluidReview API backend
"""
import json
import logging
from urllib.parse import urljoin, urlparse
from datetime import timedelta

from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import smart_text
from requests_oauthlib import OAuth2Session

from klasses.models import Klass, Bootcamp
from ecommerce.models import Line, Order
from mail.api import MailgunClient
from profiles.models import Profile
from fluidreview.serializers import UserSerializer
from fluidreview.constants import WebhookParseStatus
from fluidreview.models import OAuthToken, WebhookRequest
from fluidreview.utils import utc_now

log = logging.getLogger(__name__)

BASE_API_URL = urljoin(settings.FLUIDREVIEW_BASE_URL, '/api/v2/')


class FluidReviewException(Exception):
    """
    Custom exception for FluidReview
    """


class FluidReviewAPI:
    """
    Class for making authorized requests to the FluidReview API via OAuth2
    """

    def __init__(self):
        """
        Prepare to make OAuth2 requests to the API
        """
        self.session = self.initialize_session()

    def initialize_session(self):
        """
        Initialize an OAuth2 session with an auto-refreshing token.

        Returns:
            OAuth2Session: an OAuth2 session
        """
        token = self.get_token()
        extra = {
            'client_id': settings.FLUIDREVIEW_CLIENT_ID,
            'client_secret': settings.FLUIDREVIEW_CLIENT_SECRET,
        }
        return OAuth2Session(settings.FLUIDREVIEW_CLIENT_ID,
                             token=token,
                             auto_refresh_kwargs=extra,
                             auto_refresh_url=urljoin(BASE_API_URL, 'o/token/'),
                             token_updater=self.save_token)

    def get_token(self):
        """
        Return an OAuth token for the API. Search for an OAuthToken model first,
        and if not found then seed from the initial settings.

        Returns:
            dict: OAuthToken model instance in JSON format

        """
        token = OAuthToken.objects.first()
        if not token:
            token = OAuthToken.objects.create(
                access_token=settings.FLUIDREVIEW_ACCESS_TOKEN,
                refresh_token=settings.FLUIDREVIEW_REFRESH_TOKEN,
                token_type='Bearer',
                expires_on=utc_now()
            )
        return token.json

    def save_token(self, new_token):
        """
        Create or update the FluidReview token parameters.
        Should be automatically called when a new token is required.
        With the FluidReview API, the refresh token can only be used once and is then invalidated,
        so it must be saved and updated in the database.

        Args:
            new_token(dict): New token sent by the FluidReview API

        Returns:
            OAuthToken: the saved object

        """
        token, _ = OAuthToken.objects.get_or_create(id=1)
        token.access_token = new_token['access_token']
        token.refresh_token = new_token['refresh_token']
        # Shave 10 seconds off the expiration time just to be cautious.
        token.expires_on = utc_now() + timedelta(seconds=new_token['expires_in']-10)
        token.token_type = new_token['token_type'] or 'Bearer'
        token.save()
        return token

    def get(self, url_suffix, **kwargs):
        """
        Make a GET request to the API

        Args:
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            requests.Response: The API response
        """
        return self.request('get', url_suffix, **kwargs)

    def post(self, url_suffix, **kwargs):
        """
        Make a POST request to the API

        Args:
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            requests.Response: The API response
        """
        return self.request('post', url_suffix, **kwargs)

    def put(self, url_suffix, **kwargs):
        """
        Make a PUT request to the API

        Args:
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            requests.Response: The API response
        """
        return self.request('put', url_suffix, **kwargs)

    def request(self, method, url_suffix, **kwargs):
        """
        Make a request to the API using the designated method (GET, POST, PUT)

        Args:
            method(str): The method of the request
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            requests.Response: The API response
        """
        if url_suffix and url_suffix.startswith('/'):
            url_suffix = url_suffix[1:]
        response = getattr(self.session, method)(urljoin(BASE_API_URL, url_suffix), **kwargs)
        if response.status_code == 401:
            # The session is no longer valid, possibly a new token has been retrieved and
            # saved to the database by another instance. Re-initialize session and try again.
            self.session = self.initialize_session()
            response = getattr(self.session, method)(urljoin(BASE_API_URL, url_suffix), **kwargs)
        response.raise_for_status()
        return response


def process_user(fluid_user):
    """
    Create/update User and Profile model objects based on FluidReview user info

    Args:
        fluid_user (ReturnDict): Data from a fluidreview.serializers.UserSerializer object

    Returns:
        User: user modified or created by the function
    """
    user, _ = User.objects.get_or_create(
        email__iexact=fluid_user['email'],
        defaults={'email': fluid_user['email'], 'username': fluid_user['email']}
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.fluidreview_id:
        profile.fluidreview_id = fluid_user['id']
        profile.name = fluid_user['full_name']
        profile.save()
    return user


def parse_webhook(webhook):
    """
    Attempt to load a WebhookRequest body as JSON and assign its values to other attributes.

    Args:
        webhook (WebhookRequest): WebhookRequest instance

    """
    try:  # pylint:disable=too-many-nested-blocks
        body_json = json.loads(smart_text(webhook.body))
        required_fields = ('user_email', 'user_id')
        optional_fields = ('submission_id', 'award_id', 'award_name', 'award_cost', 'amount_to_pay')
        if not set(required_fields).issubset(body_json.keys()):
            raise FluidReviewException("Missing required field(s)")
        for att in required_fields + optional_fields:
            if att in body_json:
                if att in ('award_cost', 'amount_to_pay'):
                    if body_json[att]:
                        setattr(webhook, att, Decimal(body_json[att]))
                elif att in ('user_id', 'award_id'):
                    if body_json[att]:
                        setattr(webhook, att, int(body_json[att]))
                else:
                    setattr(webhook, att, body_json[att])
        parse_webhook_user(webhook)
        webhook.status = WebhookParseStatus.SUCCEEDED
    except:  # pylint: disable=bare-except
        webhook.status = WebhookParseStatus.FAILED
        log.exception('Webhook %s is missing values for award_cost and/or amount_to_pay', webhook.id)
    finally:
        webhook.save()


def parse_webhook_user(webhook):
    """
    Create/update User and Profile objects if necessary for a FluidReview user id
    Args:
        webhook(WebhookRequest): a WebHookRequest object
    """
    if webhook.user_id is None:
        raise FluidReviewException('user_id is required in WebhookRequest')
    profile = Profile.objects.filter(fluidreview_id=webhook.user_id).first()
    if not profile:
        # Get user info from FluidReview API (ensures that user id is real).
        user_info = FluidReviewAPI().get('/users/{}'.format(webhook.user_id)).json()
        serializer = UserSerializer(data=user_info)
        serializer.is_valid(raise_exception=True)
        user = process_user(serializer.data)
    else:
        user = profile.user
    if webhook.award_id is not None:
        personal_price = webhook.award_cost if webhook.amount_to_pay is None else webhook.amount_to_pay
        klass = Klass.objects.filter(klass_key=webhook.award_id).first()
        if not klass:
            if not personal_price:
                raise FluidReviewException(
                    f"Webhook has no personal price and klass_key {webhook.award_id} does not exist"
                )
            klass_info = FluidReviewAPI().get('/awards/{}'.format(webhook.award_id)).json()
            bootcamp = Bootcamp.objects.create(title=klass_info['name'])
            klass = Klass.objects.create(
                bootcamp=bootcamp,
                title=klass_info['description'],
                klass_key=klass_info['id'])
            try:
                MailgunClient().send_individual_email(
                    "Klass and Bootcamp created, for klass_key {klass_key}".format(
                        klass_key=klass_info['id']
                    ),
                    "Klass and Bootcamp created, for klass_key {klass_key}".format(
                        klass_key=klass_info['id']
                    ),
                    settings.EMAIL_SUPPORT
                )
            except:  # pylint: disable=bare-except
                log.exception(
                    "Error occurred when sending the email to notify "
                    "about Klass and Bootcamp creation for klass key %s",
                    klass_info['id']
                )
        if personal_price is not None:
            user.klass_prices.update_or_create(
                klass=klass,
                defaults={'price': personal_price}
            )
        else:
            user.klass_prices.filter(klass=klass).delete()


def list_users():
    """
    Generator for all users in FluidReview

    Yields:
        dict: FluidReview user as dict

    """
    frapi = FluidReviewAPI()
    url = 'users'
    while url:
        response = frapi.get(url).json()
        users = response['results']
        for fluid_user in users:
            yield fluid_user
        next_page = urlparse(response['next']).query
        url = 'users?{}'.format(next_page) if next_page else None


def post_payment(order):
    """
    Update amount paid by a user for a class when an order is fulfilled.

    Args:
        order(Order): the Order object to send payment info about to FluidReview

    """
    if order.status != Order.FULFILLED:
        return
    klass = order.get_klass()
    user = order.user
    if not klass or klass.bootcamp.legacy:
        return
    total_paid = Line.total_paid_for_klass(order.user, klass.klass_key).get('total') or Decimal('0.00')
    payment_metadata = {
        'value': '{:0.2f}'.format(total_paid)
    }
    webhook = WebhookRequest.objects.filter(user_id=user.profile.fluidreview_id, award_id=klass.klass_key).last()
    if webhook.submission_id is None:
        raise FluidReviewException(f"Webhook has no submission id for order {order.id}")
    try:
        FluidReviewAPI().put(
            'submissions/{}/metadata/{}/'.format(webhook.submission_id, settings.FLUIDREVIEW_AMOUNTPAID_ID),
            data=payment_metadata
        )
    except Exception as exc:
        raise FluidReviewException(
            f"Error updating amount paid by user {user.email} to class {klass.klass_key}"
        ) from exc
