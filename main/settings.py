"""
Django settings for ui pp. This is just a harness type
project for testing and interacting with the app.


For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

"""
import logging
import os
import platform
from urllib.parse import urljoin, urlparse

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from django.core.files.temp import NamedTemporaryFile
import dj_database_url
import saml2
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_PERSISTENT
from saml2.sigver import get_xmlsec_binary

from main.envs import get_string, get_bool, get_int, get_list, get_any
from main.sentry import init_sentry


VERSION = "0.57.4"

ENVIRONMENT = get_string(
    "BOOTCAMP_ENVIRONMENT",
    "dev",
    description="The execution environment that the app is in (e.g. dev, staging, prod)",
)
# initialize Sentry before doing anything else so we capture any config errors
SENTRY_DSN = get_string(
    "SENTRY_DSN", "", description="The connection settings for Sentry"
)
SENTRY_LOG_LEVEL = get_string(
    "SENTRY_LOG_LEVEL", "ERROR", description="The log level for Sentry"
)
init_sentry(
    dsn=SENTRY_DSN, environment=ENVIRONMENT, version=VERSION, log_level=SENTRY_LOG_LEVEL
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_string(
    "SECRET_KEY",
    "36boam8miiz0c22il@3&gputb=wrqr2plah=0#0a_bknw9(2^r",
    description="Django secret key.",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool("DEBUG", False, dev_only=True)

# Disabling the protection added in 1.10.3 against a DNS rebinding vulnerability:
# https://docs.djangoproject.com/en/1.10/releases/1.10.3/#dns-rebinding-vulnerability-when-debug-true
# Because we never debug against production data, we are not vulnerable
# to this problem.
ALLOWED_HOSTS = get_list(
    "ALLOWED_HOSTS",
    ["*"] if DEBUG else [],
    description="Allowed hosts to addres DNS rebinding vulnerability",
)

SECURE_SSL_REDIRECT = get_bool(
    "BOOTCAMP_SECURE_SSL_REDIRECT",
    True,
    description="Application-level SSL redirect setting",
)

ZENDESK_CONFIG = {
    "HELP_WIDGET_ENABLED": get_bool("ZENDESK_HELP_WIDGET_ENABLED", False),
    "HELP_WIDGET_KEY": get_string(
        "ZENDESK_HELP_WIDGET_KEY", "d99f12ec-89dd-4111-b5ea-7b36d01bba24"
    ),
}

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [r".+\.hot-update\.+", r".+\.js\.map"],
    }
}


# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "rest_framework.authtoken",
    "server_status",
    "social_django",
    "mathfilters",
    # Hijack
    "hijack",
    "compat",
    "hijack_admin",
    # other third party APPS
    # wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.settings",
    "modelcluster",
    "taggit",
    "django_filters",
    "rest_framework_serializer_extensions",
    "djangosaml2idp",
    # Our INSTALLED_APPS
    "backends",
    "main",
    "cms",
    "ecommerce",
    "mail",
    "klasses",
    "profiles",
    "applications",
    "hubspot",
    "authentication",
    "compliance",
    "jobma",
    "novoed",
)

DISABLE_WEBPACK_LOADER_STATS = get_bool(
    "DISABLE_WEBPACK_LOADER_STATS", False, dev_only=True
)
if not DISABLE_WEBPACK_LOADER_STATS:
    INSTALLED_APPS += ("webpack_loader",)

# Only include the seed data app if this isn't running in prod
if ENVIRONMENT not in ("production", "prod"):
    INSTALLED_APPS += ("localdev.seed",)

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "wagtail.core.middleware.SiteMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "main.middleware.CachelessAPIMiddleware",
)

# enable the nplusone profiler only in debug mode
if DEBUG:
    INSTALLED_APPS += ("nplusone.ext.django",)
    MIDDLEWARE += ("nplusone.ext.django.NPlusOneMiddleware",)

AUTHENTICATION_BACKENDS = (
    "backends.edxorg.EdxOrgOAuth2",
    "social_core.backends.email.EmailAuth",
    # the following needs to stay here to allow login of local users
    "django.contrib.auth.backends.ModelBackend",
)

SESSION_ENGINE_BACKEND = get_string(
    "SESSION_ENGINE_BACKEND",
    "signed_cookies",
    description=(
        "The backend that will support user sessions. This should be a module within django.contrib.sessions.backends. "
        "Possible values: signed_cookies, db, cached_db, cache, file. "
        "(https://docs.djangoproject.com/en/3.1/topics/http/sessions/#configuring-the-session-engine)"
    ),
    required=False,
)
SESSION_ENGINE = f"django.contrib.sessions.backends.{SESSION_ENGINE_BACKEND}"

# the full URL of the current application is mandatory
BOOTCAMP_ECOMMERCE_BASE_URL = get_string(
    "BOOTCAMP_ECOMMERCE_BASE_URL",
    None,
    description="The base url of this application to be used in emails",
    required=True,
)
SITE_BASE_URL = BOOTCAMP_ECOMMERCE_BASE_URL
SUPPORT_URL = get_string(
    "BOOTCAMP_SUPPORT_URL",
    "https://mitbootcamps.zendesk.com/hc/en-us/requests/new",
    description="URL for customer support",
    required=False,
)

EDXORG_BASE_URL = get_string(
    "EDXORG_BASE_URL",
    "https://courses.edx.org/",
    description="The base URL of the edX instance to use for logging in.",
    required=True,
)

# use our own strategy because our pipeline is dependent on methods defined there
SOCIAL_AUTH_STRATEGY = "authentication.strategy.DefaultStrategy"
SOCIAL_AUTH_PIPELINE = (
    # Checks if an admin user attempts to login/register while hijacking another user.
    "authentication.pipeline.user.forbid_hijack",
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    # Associates the current social details with another user account with the same email address.
    "social_core.pipeline.social_auth.associate_by_email",
    # validate an incoming email auth request
    "authentication.pipeline.user.validate_email_auth_request",
    # require a password and profile if they're not set
    "authentication.pipeline.user.validate_password",
    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    "social_core.pipeline.mail.mail_validation",
    # Send the email address and hubspot cookie if it exists to hubspot.
    "authentication.pipeline.user.send_user_to_hubspot",
    # Generate a username for the user
    # NOTE: needs to be right before create_user so nothing overrides the username
    "authentication.pipeline.user.get_username",
    # Create a user if one doesn't exist, and require a password and name
    "authentication.pipeline.user.create_user_via_email",
    # get a username for edx
    "social_core.pipeline.user.get_username",
    # create a user the old fashioned way (for edX)
    "social_core.pipeline.user.create_user",
    # verify the user against export compliance
    "authentication.pipeline.compliance.verify_exports_compliance",
    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",
    # activate the user
    "authentication.pipeline.user.activate_user",
    # Create a profile
    # NOTE: must be after all user records are created and the user is activated
    "authentication.pipeline.user.create_profile",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # this needs to be right before user_details
    "backends.pipeline_api.set_last_update",
    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
    # fetch data from edx for those users
    "backends.pipeline_api.update_profile_from_edx",
)

SOCIAL_AUTH_LOGIN_ERROR_URL = "login"
SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = [urlparse(BOOTCAMP_ECOMMERCE_BASE_URL).netloc]

SOCIAL_AUTH_EDXORG_KEY = get_string(
    "EDXORG_CLIENT_ID",
    "",
    description="The OAuth client ID configured in the edX instance",
    required=True,
)
SOCIAL_AUTH_EDXORG_SECRET = get_string(
    "EDXORG_CLIENT_SECRET",
    "",
    description="The OAuth client secret configured in the edX instance",
    required=True,
)
SOCIAL_AUTH_EDXORG_AUTH_EXTRA_ARGUMENTS = {
    "access_type": "offline",
    "approval_prompt": "auto",
}
SOCIAL_AUTH_EDXORG_EXTRA_DATA = ["updated_at"]

# Email backend settings
SOCIAL_AUTH_EMAIL_FORM_URL = "login"
SOCIAL_AUTH_EMAIL_FORM_HTML = "login.html"

SOCIAL_AUTH_EMAIL_USER_FIELDS = ["username", "email", "name", "password"]

# Only validate emails for the email backend
SOCIAL_AUTH_EMAIL_FORCE_EMAIL_VALIDATION = True

# Configure social_core.pipeline.mail.mail_validation
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = (
    "mail.v2.verification_api.send_verification_email"
)
SOCIAL_AUTH_EMAIL_VALIDATION_URL = "/"

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/signin/"
LOGIN_ERROR_URL = "/"
LOGOUT_REDIRECT_URL = "/"

AUTH_CHANGE_EMAIL_TTL_IN_MINUTES = get_int(
    "AUTH_CHANGE_EMAIL_TTL_IN_MINUTES",
    60 * 24,
    description="Expiry time for a change email request, default is 1440 minutes(1 day)",
)

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR + "/templates/"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "main.context_processors.api_keys",
                "main.context_processors.configuration_context",
                "main.context_processors.js_settings",
            ]
        },
    }
]

WSGI_APPLICATION = "main.wsgi.application"

# Hijack
HIJACK_ALLOW_GET_REQUESTS = True
HIJACK_LOGOUT_REDIRECT_URL = "/admin/auth/user"

# Database
# https://github.com/kennethreitz/dj-database-url
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DEFAULT_DATABASE_CONFIG = dj_database_url.parse(
    get_string(
        "DATABASE_URL",
        "sqlite:///{0}".format(os.path.join(BASE_DIR, "db.sqlite3")),
        description="The connection url to the Postgres database",
        required=True,
        write_app_json=False,
    )
)
DEFAULT_DATABASE_CONFIG["CONN_MAX_AGE"] = get_int(
    "BOOTCAMP_DB_CONN_MAX_AGE",
    0,
    description="The maximum age of database connections",
    required=True,
)

if get_bool(
    "BOOTCAMP_DB_DISABLE_SSL",
    False,
    description="Disables SSL to postgres if set to True",
):
    DEFAULT_DATABASE_CONFIG["OPTIONS"] = {}
else:
    DEFAULT_DATABASE_CONFIG["OPTIONS"] = {"sslmode": "require"}

DATABASES = {"default": DEFAULT_DATABASE_CONFIG}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# Serve static files with dj-static
STATIC_URL = "/static/"
CLOUDFRONT_DIST = get_string(
    "CLOUDFRONT_DIST", None, description="The cloudfront distribution for the app"
)
if CLOUDFRONT_DIST:
    STATIC_URL = urljoin(
        "https://{dist}.cloudfront.net".format(dist=CLOUDFRONT_DIST), STATIC_URL
    )

STATIC_ROOT = "staticfiles"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly"
    ],
    "COERCE_DECIMAL_TO_STRING": False,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Request files from the webpack dev server
USE_WEBPACK_DEV_SERVER = get_bool(
    "BOOTCAMP_USE_WEBPACK_DEV_SERVER", False, dev_only=True
)
WEBPACK_DEV_SERVER_HOST = get_string("WEBPACK_DEV_SERVER_HOST", "", dev_only=True)
WEBPACK_DEV_SERVER_PORT = get_string("WEBPACK_DEV_SERVER_PORT", "8098", dev_only=True)

# Important to define this so DEBUG works properly
INTERNAL_IPS = (get_string("HOST_IP", "127.0.0.1", dev_only=True),)

# Configure e-mail settings
EMAIL_BACKEND = get_string(
    "BOOTCAMP_EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
    description="The backend for email sending",
)
EMAIL_HOST = get_string(
    "BOOTCAMP_EMAIL_HOST", "localhost", description="Outgoing e-mail host"
)
EMAIL_PORT = get_int("BOOTCAMP_EMAIL_PORT", 25, description="Outgoing e-mail port")
EMAIL_HOST_USER = get_string(
    "BOOTCAMP_EMAIL_USER", "", description="Outgoing e-mail user"
)
EMAIL_HOST_PASSWORD = get_string(
    "BOOTCAMP_EMAIL_PASSWORD", "", description="Outgoing e-mail password"
)
EMAIL_USE_TLS = get_bool(
    "BOOTCAMP_EMAIL_TLS", False, description="Outgoing e-mail enable TLS"
)
EMAIL_SUPPORT = get_string(
    "BOOTCAMP_SUPPORT_EMAIL",
    "support@example.com",
    description="Email address listed for customer support",
)
DEFAULT_FROM_EMAIL = get_string(
    "BOOTCAMP_FROM_EMAIL",
    "webmaster@localhost",
    description="Default FROM email address",
)
ECOMMERCE_EMAIL = get_string(
    "BOOTCAMP_ECOMMERCE_EMAIL",
    "support@example.com",
    description="Email to send ecommerce alerts to",
)
MAILGUN_URL = get_string(
    "MAILGUN_URL",
    "https://api.mailgun.net/v3/micromasters.odl.mit.edu",
    description="The API url for mailfun",
)
MAILGUN_KEY = get_string(
    "MAILGUN_KEY",
    None,
    description="The token for authenticating against the Mailgun API",
    required=True,
)
MAILGUN_BATCH_CHUNK_SIZE = get_int(
    "MAILGUN_BATCH_CHUNK_SIZE",
    1000,
    description="Maximum number of emails to send in a batch",
)
MAILGUN_RECIPIENT_OVERRIDE = get_string(
    "MAILGUN_RECIPIENT_OVERRIDE", None, dev_only=True
)
MAILGUN_FROM_EMAIL = get_string(
    "MAILGUN_FROM_EMAIL",
    "no-reply@bootcamp.mit.edu",
    description="Email which mail comes from",
)
MAILGUN_BCC_TO_EMAIL = get_string(
    "MAILGUN_BCC_TO_EMAIL",
    "no-reply@bootcamp.mit.edu",
    description="Email which gets BCC'd on outgoing email",
)

MAILGUN_SENDER_DOMAIN = get_string(
    "MAILGUN_SENDER_DOMAIN",
    None,
    description="The domain to send mailgun email through",
    required=True,
)

BOOTCAMP_REPLY_TO_ADDRESS = get_string(
    "BOOTCAMP_REPLY_TO_ADDRESS",
    "webmaster@localhost",
    description="E-mail to use for reply-to address of emails",
)

# e-mail configurable admins
ADMIN_EMAIL = get_string(
    "BOOTCAMP_ADMIN_EMAIL", "", description="E-mail to send 500 reports to"
)
if ADMIN_EMAIL != "":
    ADMINS = (("Admins", ADMIN_EMAIL),)
else:
    ADMINS = ()

NOTIFICATION_EMAIL_BACKEND = get_string(
    "BOOTCAMP_NOTIFICATION_EMAIL_BACKEND",
    "anymail.backends.mailgun.EmailBackend",
    description="The email backend for notifications",
)

ANYMAIL = {
    "MAILGUN_API_KEY": MAILGUN_KEY,
    "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN,
}

# Logging configuration
LOG_LEVEL = get_string(
    "BOOTCAMP_LOG_LEVEL", "INFO", description="The logging level for the application"
)
DJANGO_LOG_LEVEL = get_string(
    "DJANGO_LOG_LEVEL", "DEBUG", description="The log level for Django"
)
ES_LOG_LEVEL = get_string(
    "ES_LOG_LEVEL", "INFO", description="The log level for elasticsearch"
)

# For logging to a remote syslog host
LOG_HOST = get_string("BOOTCAMP_LOG_HOST", "localhost", write_app_json=False)
LOG_HOST_PORT = get_int("BOOTCAMP_LOG_HOST_PORT", 514, write_app_json=False)

HOSTNAME = platform.node().split(".")[0]

# nplusone profiler logger configuration
NPLUSONE_LOGGER = logging.getLogger("nplusone")
NPLUSONE_LOG_LEVEL = logging.ERROR

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": (
                "[%(asctime)s] %(levelname)s %(process)d [%(name)s] "
                "%(filename)s:%(lineno)d - "
                "[{hostname}] - %(message)s"
            ).format(hostname=HOSTNAME),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "syslog": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.SysLogHandler",
            "facility": "local7",
            "formatter": "verbose",
            "address": (LOG_HOST, LOG_HOST_PORT),
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "propagate": True,
            "level": DJANGO_LOG_LEVEL,
            "handlers": ["console", "syslog"],
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": True,
        },
        "urllib3": {"level": "INFO"},
        "elasticsearch": {"level": ES_LOG_LEVEL},
        "nplusone": {"handlers": ["console"], "level": "ERROR"},
    },
    "root": {"handlers": ["console", "syslog"], "level": LOG_LEVEL},
}

# to run the app locally on mac you need to bypass syslog
if get_bool("BOOTCAMP_BYPASS_SYSLOG", False, write_app_json=False):
    LOGGING["handlers"].pop("syslog")
    LOGGING["loggers"]["root"]["handlers"] = ["console"]
    LOGGING["loggers"]["ui"]["handlers"] = ["console"]
    LOGGING["loggers"]["django"]["handlers"] = ["console"]

# server-status
STATUS_TOKEN = get_string(
    "STATUS_TOKEN", "", description="Token to access the status API.", required=True
)
HEALTH_CHECK = ["CELERY", "REDIS", "POSTGRES", "ELASTIC_SEARCH"]

ADWORDS_CONVERSION_ID = get_string(
    "ADWORDS_CONVERSION_ID", "", description="Id for adwords conversion"
)
GA_TRACKING_ID = get_string(
    "GA_TRACKING_ID", "", description="Google Analytics tracking ID"
)
GTM_TRACKING_ID = get_string(
    "GTM_TRACKING_ID", "", description="Google Tag Manager tracking ID"
)
SL_TRACKING_ID = get_string("SL_TRACKING_ID", "", description="The SL tracking ID")
REACT_GA_DEBUG = get_bool("REACT_GA_DEBUG", False, dev_only=True)

USE_X_FORWARDED_HOST = get_bool(
    "USE_X_FORWARDED_HOST",
    False,
    description="Set HOST header to original domain accessed by user",
)
SITE_NAME = get_string(
    "SITE_NAME", "MIT Bootcamp-Ecommerce", description="The site name for the app"
)
WAGTAIL_SITE_NAME = SITE_NAME

MEDIA_ROOT = get_string(
    "MEDIA_ROOT",
    os.path.join(BASE_DIR, "media"),
    description="Django MEDIA_ROOT setting",
)
MEDIA_URL = "/media/"

BOOTCAMP_ECOMMERCE_USE_S3 = get_bool(
    "BOOTCAMP_USE_S3",
    False,
    description="Use S3 for storage backend (required on Heroku)",
)
AWS_ACCESS_KEY_ID = get_string(
    "AWS_ACCESS_KEY_ID", False, description="AWS Access Key for S3 storage."
)
AWS_SECRET_ACCESS_KEY = get_string(
    "AWS_SECRET_ACCESS_KEY", False, description="AWS Secret Key for S3 storage."
)
AWS_STORAGE_BUCKET_NAME = get_string(
    "AWS_STORAGE_BUCKET_NAME", False, description="S3 Bucket name."
)
AWS_S3_FILE_OVERWRITE = get_bool("AWS_S3_FILE_OVERWRITE", False, dev_only=True)
AWS_QUERYSTRING_AUTH = get_string("AWS_QUERYSTRING_AUTH", False, write_app_json=False)
# Provide nice validation of the configuration
if BOOTCAMP_ECOMMERCE_USE_S3 and (
    not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_STORAGE_BUCKET_NAME
):
    raise ImproperlyConfigured(
        "You have enabled S3 support, but are missing one of "
        "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, or "
        "AWS_STORAGE_BUCKET_NAME"
    )
if BOOTCAMP_ECOMMERCE_USE_S3:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

MAX_FILE_UPLOAD_MB = get_int(
    "MAX_FILE_UPLOAD_MB",
    10,
    description="The maximum size in megabytes for an uploaded file",
)

# Celery
REDISCLOUD_URL = get_string(
    "REDISCLOUD_URL", None, description="RedisCloud connection url"
)

CELERY_BROKER_URL = get_string(
    "CELERY_BROKER_URL",
    REDISCLOUD_URL,
    description="Where celery should get tasks, default is Redis URL",
)
CELERY_TASK_ALWAYS_EAGER = get_string("CELERY_TASK_ALWAYS_EAGER", False, dev_only=True)
CELERY_TASK_EAGER_PROPAGATES = get_string(
    "CELERY_TASK_EAGER_PROPAGATES", True, dev_only=True
)
CELERY_RESULT_BACKEND = get_string(
    "CELERY_RESULT_BACKEND",
    REDISCLOUD_URL,
    description="Where celery should put task results, default is Redis URL",
)
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULE = {
    "check-for-hubspot-sync-errors": {
        "task": "hubspot.tasks.check_hubspot_api_errors",
        "schedule": get_int(
            "HUBSPOT_LINE_RESYNC_FREQUENCY",
            900,
            description="How often in seconds to check for hubspot errors",
        ),
    },
    "recreate-stale-interview-links": {
        "task": "applications.tasks.refresh_pending_interview_links",
        "schedule": crontab(minute=0, hour=5),
    },
}
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
USE_CELERY = True

# django cache back-ends
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}


# Cybersource
CYBERSOURCE_ACCESS_KEY = get_string(
    "CYBERSOURCE_ACCESS_KEY", None, description="CyberSource Access Key"
)
CYBERSOURCE_SECURITY_KEY = get_string(
    "CYBERSOURCE_SECURITY_KEY", None, description="CyberSource API key"
)
CYBERSOURCE_SECURE_ACCEPTANCE_URL = get_string(
    "CYBERSOURCE_SECURE_ACCEPTANCE_URL", None, description="CyberSource API endpoint"
)
CYBERSOURCE_PROFILE_ID = get_string(
    "CYBERSOURCE_PROFILE_ID", None, description="CyberSource Profile ID"
)
CYBERSOURCE_WSDL_URL = get_string(
    "CYBERSOURCE_WSDL_URL", None, description="The URL to the cybersource WSDL"
)
CYBERSOURCE_MERCHANT_ID = get_string(
    "CYBERSOURCE_MERCHANT_ID", None, description="The cybersource merchant id"
)
CYBERSOURCE_REFERENCE_PREFIX = get_string(
    "CYBERSOURCE_REFERENCE_PREFIX",
    None,
    description="a string prefix to identify the application in CyberSource transactions",
)
CYBERSOURCE_TRANSACTION_KEY = get_string(
    "CYBERSOURCE_TRANSACTION_KEY", None, description="The cybersource transaction key"
)
CYBERSOURCE_INQUIRY_LOG_NACL_ENCRYPTION_KEY = get_string(
    "CYBERSOURCE_INQUIRY_LOG_NACL_ENCRYPTION_KEY",
    None,
    description="The public key to encrypt export results with for our own security purposes. Should be a base64 encoded NaCl public key.",
)
CYBERSOURCE_EXPORT_SERVICE_ADDRESS_OPERATOR = get_string(
    "CYBERSOURCE_EXPORT_SERVICE_ADDRESS_OPERATOR",
    "AND",
    description="Whether just the name or the name and address should be used in exports verification. Refer to Cybersource docs.",
)
CYBERSOURCE_EXPORT_SERVICE_ADDRESS_WEIGHT = get_string(
    "CYBERSOURCE_EXPORT_SERVICE_ADDRESS_WEIGHT",
    "high",
    description="The weight of the address in determining whether a user passes exports checks. Refer to Cybersource docs.",
)
CYBERSOURCE_EXPORT_SERVICE_NAME_WEIGHT = get_string(
    "CYBERSOURCE_EXPORT_SERVICE_NAME_WEIGHT",
    "high",
    description="The weight of the name in determining whether a user passes exports checks. Refer to Cybersource docs.",
)

CYBERSOURCE_EXPORT_SERVICE_SANCTIONS_LISTS = get_string(
    "CYBERSOURCE_EXPORT_SERVICE_SANCTIONS_LISTS",
    None,
    description="Additional sanctions lists to validate for exports. Refer to Cybersource docs.",
)


# Feature flags
def get_all_config_keys():
    """Returns all the configuration keys from both environment and configuration files"""
    return list(os.environ.keys())


BOOTCAMP_FEATURES_PREFIX = get_string(
    "BOOTCAMP_FEATURES_PREFIX", "FEATURE_", write_app_json=False
)
BOOTCAMP_FEATURES_DEFAULT = get_bool("BOOTCAMP_FEATURES_DEFAULT", False, dev_only=True)
FEATURES = {
    key[len(BOOTCAMP_FEATURES_PREFIX) :]: get_any(key, None, write_app_json=False)
    for key in get_all_config_keys()
    if key.startswith(BOOTCAMP_FEATURES_PREFIX)
}

MIDDLEWARE_FEATURE_FLAG_COOKIE_NAME = get_string(
    "MIDDLEWARE_FEATURE_FLAG_COOKIE_NAME",
    "BC_FEATURE_FLAGS",
    description="Feature flag cookiename",
)
MIDDLEWARE_FEATURE_FLAG_COOKIE_MAX_AGE_SECONDS = get_int(
    "MIDDLEWARE_FEATURE_FLAG_COOKIE_MAX_AGE_SECONDS",
    60 * 60,
    description="Maximum age for feature flag cookies",
)


# django debug toolbar only in debug mode
if DEBUG:
    INSTALLED_APPS += ("debug_toolbar",)
    # it needs to be enabled before other middlewares
    MIDDLEWARE = ("debug_toolbar.middleware.DebugToolbarMiddleware",) + MIDDLEWARE

HUBSPOT_API_KEY = get_string("HUBSPOT_API_KEY", "", description="API key for Hubspot")
HUBSPOT_ID_PREFIX = get_string(
    "HUBSPOT_ID_PREFIX", "bootcamp", description="Hub spot id prefix."
)

HUBSPOT_CONFIG = {
    "HUBSPOT_NEW_COURSES_FORM_GUID": get_string(
        "HUBSPOT_NEW_COURSES_FORM_GUID",
        None,
        description="Form guid over hub spot for new courses email subscription form.",
    ),
    "HUBSPOT_FOOTER_FORM_GUID": get_string(
        "HUBSPOT_FOOTER_FORM_GUID",
        None,
        description="Form guid over hub spot for footer block.",
    ),
    "HUBSPOT_PORTAL_ID": get_string(
        "HUBSPOT_PORTAL_ID", None, description="Hub spot portal id."
    ),
    "HUBSPOT_CREATE_USER_FORM_ID": get_string(
        "HUBSPOT_CREATE_USER_FORM_ID", None, description="Form ID for Hubspot Forms API"
    ),
}

RECAPTCHA_SITE_KEY = get_string(
    "RECAPTCHA_SITE_KEY", "", description="The ReCaptcha site key"
)
RECAPTCHA_SECRET_KEY = get_string(
    "RECAPTCHA_SECRET_KEY", "", description="The ReCaptcha secret key"
)

JOBMA_BASE_URL = get_string(
    "JOBMA_BASE_URL", "", description="The base URL for accessing Jobma"
)
JOBMA_ACCESS_TOKEN = get_string(
    "JOBMA_ACCESS_TOKEN",
    "",
    description="The JOBMA access token used to access their REST API",
)
JOBMA_WEBHOOK_ACCESS_TOKEN = get_string(
    "JOBMA_WEBHOOK_ACCESS_TOKEN",
    "",
    description="The Jobma access token used by us to verify that a postback came from Jobma",
)
JOBMA_LINK_EXPIRATION_DAYS = get_int(
    "JOBMA_LINK_EXPIRATION_DAYS",
    29,
    description="The number of days for Jobma links to expire",
)

NOVOED_API_KEY = get_string("NOVOED_API_KEY", None, description="The NovoEd API key")
NOVOED_API_SECRET = get_string(
    "NOVOED_API_SECRET", None, description="The NovoEd API secret"
)
NOVOED_API_BASE_URL = get_string(
    "NOVOED_API_BASE_URL", None, description="The base URL of the NovoEd API"
)
NOVOED_SAML_LOGIN_URL = get_string(
    "NOVOED_SAML_LOGIN_URL",
    None,
    description="The SP-initiated SAML login URL for NovoEd",
)

# Relative URL to be used by Djoser for the link in the password reset email
# (see: http://djoser.readthedocs.io/en/stable/settings.html#password-reset-confirm-url)
PASSWORD_RESET_CONFIRM_URL = "password_reset/confirm/{uid}/{token}/"

# Djoser library settings (see: http://djoser.readthedocs.io/en/stable/settings.html)
DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": PASSWORD_RESET_CONFIRM_URL,
    "SET_PASSWORD_RETYPE": False,
    "LOGOUT_ON_PASSWORD_CHANGE": False,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True,
    "EMAIL": {"password_reset": "authentication.views.CustomPasswordResetEmail"},
}

# NovoEd SAML settings (using Bootcamps app as IdP)
BOOTCAMP_ECOMMERCE_SAML_BASE_URL = get_string(
    "BOOTCAMP_ECOMMERCE_SAML_BASE_URL",
    None,
    description=(
        "(Optional) If provided, this base URL will be used instead of BOOTCAMP_ECOMMERCE_BASE_URL "
        "for SAML login/logout URLs"
    ),
)
IDP_BASE_URL = urljoin(
    BOOTCAMP_ECOMMERCE_SAML_BASE_URL or BOOTCAMP_ECOMMERCE_BASE_URL, "/idp"
)
_novoed_saml_key = get_string(
    "NOVOED_SAML_KEY",
    None,
    description="Contents of the SAML key for NovoEd ('\n' line separators)",
)
_novoed_saml_cert = get_string(
    "NOVOED_SAML_CERT",
    None,
    description="Contents of the SAML certificate for NovoEd ('\n' line separators)",
)
NOVOED_SAML_DEBUG = get_bool(
    "NOVOED_SAML_DEBUG",
    False,
    description="Flag indicating whether the SAML config should be set to debug mode",
)
NOVOED_SAML_CONFIG_TTL_HOURS = get_int(
    "NOVOED_SAML_CONFIG_TTL_HOURS",
    365 * 24,
    description="The number of hours that the SAML config is expected to be accurate",
)

if _novoed_saml_key and _novoed_saml_cert:
    with NamedTemporaryFile(prefix="saml_", suffix=".key", delete=False) as f:
        lines = _novoed_saml_key.split("\\n")
        for line in lines:
            f.write(f"{line}\n".encode("utf-8"))
        _novoed_saml_key_file_path = f.name
    with NamedTemporaryFile(prefix="saml_", suffix=".cert", delete=False) as f:
        lines = _novoed_saml_cert.split("\\n")
        for line in lines:
            f.write(f"{line}\n".encode("utf-8"))
        _novoed_saml_cert_file_path = f.name
    SAML_IDP_CONFIG = {
        "debug": NOVOED_SAML_DEBUG,
        "xmlsec_binary": get_xmlsec_binary(
            ["/usr/bin/xmlsec1", "/usr/local/bin/xmlsec1"]
        ),
        "entityid": f"{IDP_BASE_URL}/metadata",
        "description": "MIT Bootcamps",
        "service": {
            "idp": {
                "name": "Bootcamp IdP",
                "endpoints": {
                    "single_sign_on_service": [
                        (f"{IDP_BASE_URL}/sso/post", saml2.BINDING_HTTP_POST),
                        (f"{IDP_BASE_URL}/sso/redirect", saml2.BINDING_HTTP_REDIRECT),
                    ],
                    "single_logout_service": [
                        (f"{IDP_BASE_URL}/slo/post", saml2.BINDING_HTTP_POST),
                        (f"{IDP_BASE_URL}/slo/redirect", saml2.BINDING_HTTP_REDIRECT),
                    ],
                },
                "name_id_format": [NAMEID_FORMAT_UNSPECIFIED, NAMEID_FORMAT_PERSISTENT],
                "sign_response": False,
                "sign_assertion": False,
                "want_authn_requests_signed": False,
            }
        },
        # Signing
        "key_file": _novoed_saml_key_file_path,
        "cert_file": _novoed_saml_cert_file_path,
        # Encryption
        "encryption_keypairs": [
            {
                "key_file": _novoed_saml_key_file_path,
                "cert_file": _novoed_saml_cert_file_path,
            }
        ],
        "additional_cert_files": [],
        "valid_for": NOVOED_SAML_CONFIG_TTL_HOURS,
    }
