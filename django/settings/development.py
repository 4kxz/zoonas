import os

from django.core.exceptions import ImproperlyConfigured

from .base import *


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = get_env_variable('ZOONAS_DJANGO_SECRET_KEY')

# Try to run using postgres
try:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     get_env_variable('ZOONAS_DB_NAME'),
            'USER':     get_env_variable('ZOONAS_DB_USER'),
            'PASSWORD': get_env_variable('ZOONAS_DB_PASSWORD'),
            'HOST':     '0.0.0.0',
            'PORT':     '5432',
            # There was this one time when the db threw nonsense errors. This
            # somehow showed the actual error message:
            # 'OPTIONS': {'autocommit': True, },
        }
    }

# If there is no database information just run sqlite
except ImproperlyConfigured as e:
    print("ImproperlyConfigured:")
    print(e.message)
    print("Trying sqlite instead.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': path('.db', 'db.sqlite3'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

STATIC_ROOT = path('.static')
STATIC_URL = '/static/'

MEDIA_ROOT = path('.media')
MEDIA_URL = '/media/'

# ReCaptcha:
RECAPTCHA_PUBLIC_KEY = get_env_variable('ZOONAS_RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = get_env_variable('ZOONAS_RECAPTCHA_PRIVATE_KEY')

# Amazon Web Services:
AWS_ACCESS_KEY_ID = get_env_variable('ZOONAS_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_variable('ZOONAS_AWS_SECRET_ACCESS_KEY_ID')
AWS_STORAGE_BUCKET_NAME = get_env_variable('ZOONAS_AWS_STORAGE_BUCKET_NAME')

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
)

STATICFILES_DIRS += (path('.tmp'), )  # SCSS gets compiled to this folder

INTERNAL_IPS = ('127.0.0.1', )  # Used by debug toolbar

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
