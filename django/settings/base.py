import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))

def path(*x):
    return os.path.abspath(os.path.join(ROOT, '..', '..', *x))

sys.path.insert(0, path('django/apps'))

ADMINS = (
    ('Carlos', 'carlos@zoonas.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Madrid'

LANGUAGE_CODE = 'es-es'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATICFILES_DIRS = (
    path('static/css'),
    path('static/img'),
    path('static/js'),
    path('static/scss'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    # 'django.core.context_processors.media',
    'django.core.context_processors.request',
    # 'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'users.context_processors.subscribed_zone_list',
    'zones.context_processors.default_zone_list',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'misc.middleware.RedirectToNext',
)

ROOT_URLCONF = 'zoonas.urls'

WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    path('django', 'templates'),
)

LOCALE_PATHS = (
    path('django', 'locale'),
)

INSTALLED_APPS = (
    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'captcha',
    'crispy_forms',
    'djcelery',
    'storages',
    'misc',
    'users',
    'zones',
    'submissions',
    'domains',
    'votes',
    'notes',  # Stupidest name ever. Should be called messages, but that would
              # clash with the default notification app, so notes it is.
    'reports',
    'comments',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

FIXTURE_DIRS = (
    path('django', 'fixtures'),
)

# Custom user model:
AUTH_USER_MODEL = 'users.User'

# Custom login url:
LOGIN_URL = '/account/login/'

# Used by crispy forms:
CRISPY_TEMPLATE_PACK = 'bootstrap'

# Celery & Redis:
import djcelery
djcelery.setup_loader()
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Amazon S3 Storage:
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Random limits:
SUBMISSIONS_PER_PAGE = 20

# Submissions:
SUBMISSION_TITLE_LENGTH = 100
SUBMISSION_SLUG_LENGTH = 110
EDIT_TIME = 10 * 60  # In seconds.

# Zones:
ZONE_NAME_LENGTH = 20
ZONE_DESCRIPTION_LENGTH = 200
ZONE_INFORMATION_LENGTH = 2000
MODERATOR_LIMIT = 5  # Moderators allowed per zone.
ZONE_LIST_SIZE = 20  # Zones in the navigation menu.

# Users:
USER_NAME_LENGTH = 20
SUBSCRIPTION_LIMIT = 10  # Subscriptions allowed per user.

# Messages:
MESSAGE_LENGTH = 9999

# Thumbnails:
THUMBNAIL_SIZE = (110, 64)

