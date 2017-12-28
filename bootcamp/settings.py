"""
Django settings for ui pp. This is just a harness type
project for testing and interacting with the app.


For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

"""
import ast
import logging
import os
import platform
from urllib.parse import urljoin

import dj_database_url
import yaml


VERSION = "0.6.1"

CONFIG_PATHS = [
    os.environ.get('BOOTCAMP_CONFIG', ''),
    os.path.join(os.getcwd(), 'bootcamp-ecommerce.yml'),
    os.path.join(os.path.expanduser('~'), 'bootcamp-ecommerce.yml'),
    '/etc/bootcamp-ecommerce.yml',
]


def load_fallback():
    """Load optional yaml config"""
    fallback_config = {}
    config_file_path = None
    for config_path in CONFIG_PATHS:
        if os.path.isfile(config_path):
            config_file_path = config_path
            break
    if config_file_path is not None:
        with open(config_file_path) as config_file:
            fallback_config = yaml.safe_load(config_file)
    return fallback_config

FALLBACK_CONFIG = load_fallback()


def get_var(name, default):
    """Return the settings in a precedence way with default"""
    try:
        value = os.environ.get(name, FALLBACK_CONFIG.get(name, default))
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_var(
    'SECRET_KEY',
    '36boam8miiz0c22il@3&gputb=wrqr2plah=0#0a_bknw9(2^r'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_var('DEBUG', False)

if DEBUG:
    # Disabling the protection added in 1.10.3 against a DNS rebinding vulnerability:
    # https://docs.djangoproject.com/en/1.10/releases/1.10.3/#dns-rebinding-vulnerability-when-debug-true
    # Because we never debug against production data, we are not vulnerable
    # to this problem.
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = get_var('ALLOWED_HOSTS', [])

SECURE_SSL_REDIRECT = get_var('BOOTCAMP_SECURE_SSL_REDIRECT', True)


WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [
            r'.+\.hot-update\.+',
            r'.+\.js\.map'
        ]
    }
}


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'server_status',
    'social_django',

    # other third party APPS
    'raven.contrib.django.raven_compat',

    # Our INSTALLED_APPS
    'backends',
    'bootcamp',
    'ecommerce',
    'fluidreview',
    'mail',
    'klasses',
    'profiles',
)

DISABLE_WEBPACK_LOADER_STATS = get_var("DISABLE_WEBPACK_LOADER_STATS", False)
if not DISABLE_WEBPACK_LOADER_STATS:
    INSTALLED_APPS += ('webpack_loader',)


MIDDLEWARE_CLASSES = (
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

# enable the nplusone profiler only in debug mode
if DEBUG:
    INSTALLED_APPS += (
        'nplusone.ext.django',
    )
    MIDDLEWARE_CLASSES += (
        'nplusone.ext.django.NPlusOneMiddleware',
    )

AUTHENTICATION_BACKENDS = (
    'backends.edxorg.EdxOrgOAuth2',
    # the following needs to stay here to allow login of local users
    'django.contrib.auth.backends.ModelBackend',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# the full URL of the current application is mandatory
BOOTCAMP_ECOMMERCE_BASE_URL = get_var('BOOTCAMP_ECOMMERCE_BASE_URL', None)

EDXORG_BASE_URL = get_var('EDXORG_BASE_URL', 'https://courses.edx.org/')
SOCIAL_AUTH_EDXORG_KEY = get_var('EDXORG_CLIENT_ID', '')
SOCIAL_AUTH_EDXORG_SECRET = get_var('EDXORG_CLIENT_SECRET', '')
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    # the following custom pipeline func goes before load_extra_data
    'backends.pipeline_api.set_last_update',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'backends.pipeline_api.update_profile_from_edx',
)
SOCIAL_AUTH_EDXORG_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'approval_prompt': 'auto'
}
SOCIAL_AUTH_EDXORG_EXTRA_DATA = ['updated_at']

LOGIN_REDIRECT_URL = '/pay'
LOGIN_URL = '/'
LOGIN_ERROR_URL = '/'

ROOT_URLCONF = 'bootcamp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'bootcamp.context_processors.api_keys',
            ],
        },
    },
]

WSGI_APPLICATION = 'bootcamp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# Uses DATABASE_URL to configure with sqlite default:
# For URL structure:
# https://github.com/kennethreitz/dj-database-url
DEFAULT_DATABASE_CONFIG = dj_database_url.parse(
    get_var(
        'DATABASE_URL',
        'sqlite:///{0}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )
)
DEFAULT_DATABASE_CONFIG['CONN_MAX_AGE'] = int(get_var('BOOTCAMP_DB_CONN_MAX_AGE', 0))

if get_var('BOOTCAMP_DB_DISABLE_SSL', False):
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {}
else:
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {'sslmode': 'require'}

DATABASES = {
    'default': DEFAULT_DATABASE_CONFIG
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# Serve static files with dj-static
STATIC_URL = '/static/'
CLOUDFRONT_DIST = get_var('CLOUDFRONT_DIST', None)
if CLOUDFRONT_DIST:
    STATIC_URL = urljoin('https://{dist}.cloudfront.net'.format(dist=CLOUDFRONT_DIST), STATIC_URL)

STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'COERCE_DECIMAL_TO_STRING': False
}

# Request files from the webpack dev server
USE_WEBPACK_DEV_SERVER = get_var('BOOTCAMP_USE_WEBPACK_DEV_SERVER', False)
WEBPACK_DEV_SERVER_HOST = get_var('WEBPACK_DEV_SERVER_HOST', '')
WEBPACK_DEV_SERVER_PORT = get_var('WEBPACK_DEV_SERVER_PORT', '8098')

# Important to define this so DEBUG works properly
INTERNAL_IPS = (get_var('HOST_IP', '127.0.0.1'), )

# Configure e-mail settings
EMAIL_BACKEND = get_var('BOOTCAMP_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = get_var('BOOTCAMP_EMAIL_HOST', 'localhost')
EMAIL_PORT = get_var('BOOTCAMP_EMAIL_PORT', 25)
EMAIL_HOST_USER = get_var('BOOTCAMP_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = get_var('BOOTCAMP_EMAIL_PASSWORD', '')
EMAIL_USE_TLS = get_var('BOOTCAMP_EMAIL_TLS', False)
EMAIL_SUPPORT = get_var('BOOTCAMP_SUPPORT_EMAIL', 'support@example.com')
DEFAULT_FROM_EMAIL = get_var('BOOTCAMP_FROM_EMAIL', 'webmaster@localhost')
ECOMMERCE_EMAIL = get_var('BOOTCAMP_ECOMMERCE_EMAIL', 'support@example.com')
MAILGUN_URL = get_var('MAILGUN_URL', 'https://api.mailgun.net/v3/micromasters.odl.mit.edu')
MAILGUN_KEY = get_var('MAILGUN_KEY', None)
MAILGUN_BATCH_CHUNK_SIZE = get_var('MAILGUN_BATCH_CHUNK_SIZE', 1000)
MAILGUN_RECIPIENT_OVERRIDE = get_var('MAILGUN_RECIPIENT_OVERRIDE', None)
MAILGUN_FROM_EMAIL = get_var('MAILGUN_FROM_EMAIL', 'no-reply@micromasters.mit.edu')
MAILGUN_BCC_TO_EMAIL = get_var('MAILGUN_BCC_TO_EMAIL', 'no-reply@micromasters.mit.edu')

# e-mail configurable admins
ADMIN_EMAIL = get_var('BOOTCAMP_ADMIN_EMAIL', '')
if ADMIN_EMAIL is not '':
    ADMINS = (('Admins', ADMIN_EMAIL),)
else:
    ADMINS = ()

# Logging configuration
LOG_LEVEL = get_var('BOOTCAMP_LOG_LEVEL', 'INFO')
DJANGO_LOG_LEVEL = get_var('DJANGO_LOG_LEVEL', 'INFO')
SENTRY_LOG_LEVEL = get_var('SENTRY_LOG_LEVEL', 'ERROR')
ES_LOG_LEVEL = get_var('ES_LOG_LEVEL', 'INFO')

# For logging to a remote syslog host
LOG_HOST = get_var('BOOTCAMP_LOG_HOST', 'localhost')
LOG_HOST_PORT = get_var('BOOTCAMP_LOG_HOST_PORT', 514)

HOSTNAME = platform.node().split('.')[0]

# nplusone profiler logger configuration
NPLUSONE_LOGGER = logging.getLogger('nplusone')
NPLUSONE_LOG_LEVEL = logging.ERROR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s] %(levelname)s %(process)d [%(name)s] '
                '%(filename)s:%(lineno)d - '
                '[{hostname}] - %(message)s'
            ).format(hostname=HOSTNAME),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'syslog': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local7',
            'formatter': 'verbose',
            'address': (LOG_HOST, LOG_HOST_PORT)
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'sentry': {
            'level': SENTRY_LOG_LEVEL,
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'propagate': True,
            'level': DJANGO_LOG_LEVEL,
            'handlers': ['console', 'syslog'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        },
        'urllib3': {
            'level': 'INFO',
        },
        'raven': {
            'level': SENTRY_LOG_LEVEL,
            'handlers': []
        },
        'nplusone': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'syslog'],
        'level': LOG_LEVEL,
    },
}

# Sentry
ENVIRONMENT = get_var('BOOTCAMP_ENVIRONMENT', 'dev')
SENTRY_CLIENT = 'raven.contrib.django.raven_compat.DjangoClient'
RAVEN_CONFIG = {
    'dsn': get_var('SENTRY_DSN', ''),
    'environment': ENVIRONMENT,
    'release': VERSION
}

# to run the app locally on mac you need to bypass syslog
if get_var('BOOTCAMP_BYPASS_SYSLOG', False):
    LOGGING['handlers'].pop('syslog')
    LOGGING['loggers']['root']['handlers'] = ['console']
    LOGGING['loggers']['ui']['handlers'] = ['console']
    LOGGING['loggers']['django']['handlers'] = ['console']

# server-status
STATUS_TOKEN = get_var("STATUS_TOKEN", "")
HEALTH_CHECK = ['CELERY', 'REDIS', 'POSTGRES', 'ELASTIC_SEARCH']

ADWORDS_CONVERSION_ID = get_var("ADWORDS_CONVERSION_ID", "")
GA_TRACKING_ID = get_var("GA_TRACKING_ID", "")
GOOGLE_API_KEY = get_var("GOOGLE_API_KEY", "")
SL_TRACKING_ID = get_var("SL_TRACKING_ID", "")
REACT_GA_DEBUG = get_var("REACT_GA_DEBUG", False)

# Celery
CELERY_BROKER_URL = get_var(
    "CELERY_BROKER_URL", get_var("REDISCLOUD_URL", None)) or get_var("BROKER_URL", get_var("REDISCLOUD_URL", None))
CELERY_TASK_ALWAYS_EAGER = get_var("CELERY_TASK_ALWAYS_EAGER", False) or get_var("CELERY_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = get_var(
    "CELERY_TASK_EAGER_PROPAGATES", True) or get_var("CELERY_EAGER_PROPAGATES_EXCEPTIONS", True)
CELERY_RESULT_BACKEND = get_var(
    "CELERY_RESULT_BACKEND", get_var("REDISCLOUD_URL", None)
)
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {}
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
USE_CELERY = True

# django cache back-ends
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'local-in-memory-cache',
    },
    'redis': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_BROKER_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
    },
}


# Cybersource
CYBERSOURCE_ACCESS_KEY = get_var("CYBERSOURCE_ACCESS_KEY", None)
CYBERSOURCE_SECURITY_KEY = get_var("CYBERSOURCE_SECURITY_KEY", None)
CYBERSOURCE_TRANSACTION_KEY = get_var("CYBERSOURCE_TRANSACTION_KEY", None)
CYBERSOURCE_SECURE_ACCEPTANCE_URL = get_var("CYBERSOURCE_SECURE_ACCEPTANCE_URL", None)
CYBERSOURCE_PROFILE_ID = get_var("CYBERSOURCE_PROFILE_ID", None)
CYBERSOURCE_REFERENCE_PREFIX = get_var("CYBERSOURCE_REFERENCE_PREFIX", None)


# FluidReview
FLUIDREVIEW_ACCESS_TOKEN = get_var("FLUIDREVIEW_ACCESS_TOKEN", None)
FLUIDREVIEW_REFRESH_TOKEN = get_var("FLUIDREVIEW_REFRESH_TOKEN", None)
FLUIDREVIEW_CLIENT_ID = get_var("FLUIDREVIEW_CLIENT_ID", None)
FLUIDREVIEW_CLIENT_SECRET = get_var("FLUIDREVIEW_CLIENT_SECRET", None)
FLUIDREVIEW_BASE_URL = get_var("FLUIDREVIEW_BASE_URL", None)
FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = get_var("FLUIDREVIEW_WEBHOOK_AUTH_TOKEN", None)
FLUIDREVIEW_AMOUNTPAID_ID = get_var("FLUIDREVIEW_AMOUNTPAID_ID", None)

# BOOTCAMP ADMISSION
BOOTCAMP_ADMISSION_BASE_URL = get_var("BOOTCAMP_ADMISSION_BASE_URL", "http://bootcamp-admission.example.com")
BOOTCAMP_ADMISSION_KEY = get_var("BOOTCAMP_ADMISSION_KEY", "")


# features flags
def get_all_config_keys():
    """Returns all the configuration keys from both environment and configuration files"""
    return list(set(os.environ.keys()).union(set(FALLBACK_CONFIG.keys())))

BOOTCAMP_FEATURES_PREFIX = get_var('BOOTCAMP_FEATURES_PREFIX', 'FEATURE_')
FEATURES = {
    key[len(BOOTCAMP_FEATURES_PREFIX):]: get_var(key, None) for key
    in get_all_config_keys() if key.startswith(BOOTCAMP_FEATURES_PREFIX)
}

MIDDLEWARE_FEATURE_FLAG_COOKIE_NAME = get_var('MIDDLEWARE_FEATURE_FLAG_COOKIE_NAME', 'MM_FEATURE_FLAGS')
MIDDLEWARE_FEATURE_FLAG_COOKIE_MAX_AGE_SECONDS = get_var('MIDDLEWARE_FEATURE_FLAG_COOKIE_MAX_AGE_SECONDS', 60 * 60)


# django debug toolbar only in debug mode
if DEBUG:
    INSTALLED_APPS += ('debug_toolbar', )
    # it needs to be enabled before other middlewares
    MIDDLEWARE_CLASSES = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ) + MIDDLEWARE_CLASSES

MANDATORY_SETTINGS = [
    'FLUIDREVIEW_WEBHOOK_AUTH_TOKEN',
    'FLUIDREVIEW_AMOUNTPAID_ID',
    'FLUIDREVIEW_BASE_URL',
    'FLUIDREVIEW_CLIENT_ID',
    'FLUIDREVIEW_CLIENT_SECRET',
    'FLUIDREVIEW_ACCESS_TOKEN',
    'FLUIDREVIEW_REFRESH_TOKEN'
]
