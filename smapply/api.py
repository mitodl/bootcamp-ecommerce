"""
SMApply API backend
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

from klasses.models import Klass
from ecommerce.models import Line, Order
from profiles.models import Profile
from fluidreview.serializers import UserSerializer
from fluidreview.constants import WebhookParseStatus
from smapply.models import OAuthTokenSMA, WebhookRequestSMA
from fluidreview.utils import utc_now

log = logging.getLogger(__name__)

BASE_API_URL = urljoin(settings.SMAPPLY_BASE_URL, '/api/v2/')


class SMApplyException(Exception):
    """
    Custom exception for SMApply
    """


class SMApplyAPI:
    """
    Class for making authorized requests to the SMApply API via OAuth2
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
            'client_id': settings.SMAPPLY_CLIENT_ID,
            'client_secret': settings.SMAPPLY_CLIENT_SECRET,
        }
        return OAuth2Session(settings.SMAPPLY_CLIENT_ID,
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
        token = OAuthTokenSMA.objects.first()
        if not token:
            token = OAuthTokenSMA.objects.create(
                access_token=settings.SMAPPLY_ACCESS_TOKEN,
                refresh_token=settings.SMAPPLY_REFRESH_TOKEN,
                token_type='Bearer',
                expires_on=utc_now()
            )
        return token.json

    def save_token(self, new_token):
        """
        Create or update the SMApply token parameters.
        Should be automatically called when a new token is required.
        With the SMApply API, the refresh token can only be used once and is then invalidated,
        so it must be saved and updated in the database.

        Args:
            new_token(dict): New token sent by the SMApply API

        Returns:
            OAuthTokenSMA: the saved object

        """
        token, _ = OAuthTokenSMA.objects.get_or_create(id=1)
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


def process_user(sma_user):
    """
    Create/update User and Profile model objects based on SMApply user info

    Args:
        sma_user (ReturnDict): Data from a fluidreview.serializers.UserSerializer object

    Returns:
        User: user modified or created by the function
    """
    user, _ = User.objects.get_or_create(
        email__iexact=sma_user['email'],
        defaults={'email': sma_user['email'], 'username': sma_user['email']}
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.smaplly_id:
        profile.smaplly_id = sma_user['id']
        profile.name = sma_user['full_name']
        profile.save()
    return user


def parse_webhook(webhook):
    """
    Attempt to load a WebhookRequestSMA body as JSON and assign its values to other attributes.

    Args:
        webhook (WebhookRequestSMA): WebhookRequestSMA instance

    """
    try:  # pylint:disable=too-many-nested-blocks
        body_json = json.loads(smart_text(webhook.body))
        field_mapping = {'id': 'submittion_id', 'award': 'award_id', 'user_id': 'user_id'}
        required_fields = field_mapping.keys()
        if not set(required_fields).issubset(body_json.keys()):
            raise SMApplyException("Missing required field(s)")
        for att in required_fields:
            if att in body_json:
                if att in required_fields:
                    if body_json[att]:
                        setattr(webhook, att, int(body_json[att]))
                else:
                    setattr(webhook, att, body_json[att])
        parse_webhook_user(webhook)
        webhook.status = WebhookParseStatus.SUCCEEDED
    except:  # pylint: disable=bare-except
        webhook.status = WebhookParseStatus.FAILED
        log.exception('Webhook %s body is not valid JSON or has invalid/missing values.', webhook.id)
    finally:
        webhook.save()


def parse_webhook_user(webhook):
    """
    Create/update User and Profile objects if necessary for a SMApply user id
    Args:
        webhook(WebhookRequestSMA): a WebhookRequestSMA object
    """
    if webhook.user_id is None:
        raise SMApplyException('user_id is required in WebhookRequestSMA')
    profile = Profile.objects.filter(smapply_id=webhook.user_id).first()
    if not profile:
        # Get user info from FluidReview API (ensures that user id is real).
        user_info = SMApplyAPI().get('/users/{}'.format(webhook.user_id)).json()
        serializer = UserSerializer(data=user_info)
        serializer.is_valid(raise_exception=True)
        user = process_user(serializer.data)
    else:
        user = profile.user
    if webhook.award_id is not None:
        personal_price = webhook.award_cost if webhook.amount_to_pay is None else webhook.amount_to_pay
        klass = Klass.objects.get(klass_key=webhook.award_id)
        if personal_price is not None:
            user.klass_prices.update_or_create(
                klass=klass,
                defaults={'price': personal_price}
            )
        else:
            user.klass_prices.filter(klass=klass).delete()


def list_users():
    """
    Generator for all users in SMApply

    Yields:
        dict: SMApply user as dict

    """
    smapi = SMApplyAPI()
    url = 'users'
    while url:
        response = smapi.get(url).json()
        users = response['results']
        for sma_user in users:
            yield sma_user
        next_page = urlparse(response['next']).query
        url = 'users?{}'.format(next_page) if next_page else None
