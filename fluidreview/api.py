"""
FluidReview API backend
"""
from urllib.parse import urljoin
from datetime import timedelta
from django.conf import settings
from requests_oauthlib import OAuth2Session
from fluidreview.models import OAuthToken
from fluidreview.utils import utc_now


BASE_API_URL = urljoin(settings.FLUIDREVIEW_BASE_URL, '/api/v2/')


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
            dict: The API response
        """
        return self.request('get', url_suffix, **kwargs)

    def post(self, url_suffix, **kwargs):
        """
        Make a POST request to the API

        Args:
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            dict: The API response
        """
        return self.request('post', url_suffix, **kwargs)

    def put(self, url_suffix, **kwargs):
        """
        Make a PUT request to the API

        Args:
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            dict: The API response
        """
        return self.request('put', url_suffix, **kwargs)

    def request(self, method, url_suffix, **kwargs):
        """
        Make a request to the API using the designated method (GET, POST, PUT)

        Args:
            method(str): The method of the request
            url_suffix(str): The URL fragment to be appended to the base API URL

        Returns:
            dict: The API response
        """
        if url_suffix and url_suffix.startswith('/'):
            url_suffix = url_suffix[1:]
        response = getattr(self.session, method)(urljoin(BASE_API_URL, url_suffix), **kwargs)
        if response.status_code == 401:
            # The session is no longer valid, possibly a new token has been retrieved and
            # saved to the database by another instance. Re-initialize session and try again.
            self.session = self.initialize_session()
            response = getattr(self.session, method)(urljoin(BASE_API_URL, url_suffix), **kwargs)
        return response
