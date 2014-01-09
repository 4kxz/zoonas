from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = '{{ pillar["django"]["secret_key"] }}'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     '{{ pillar["postgresql"]["database"] }}',
        'USER':     '{{ pillar["postgresql"]["username"] }}',
        'PASSWORD': '{{ pillar["postgresql"]["password"] }}',
        'HOST':     '{{ pillar["postgresql"]["host"] }}',
        'PORT':     '{{ pillar["postgresql"]["port"] }}',
    }
}

STATIC_URL = '{{ pillar["django"]["static_url"] }}/'
STATIC_ROOT = '{{ pillar["path"] }}/static-files'

MEDIA_URL = '{{ pillar["django"]["media_url"] }}/'
MEDIA_ROOT = '{{ pillar["path"] }}/media-files'

# ReCaptcha:
RECAPTCHA_PUBLIC_KEY = '{{ pillar["recaptcha"]["public_key"] }}'
RECAPTCHA_PRIVATE_KEY = '{{ pillar["recaptcha"]["private_key"] }}'

# Amazon Web Services:
AWS_ACCESS_KEY_ID = '{{ pillar["aws"]["access_key"] }}'
AWS_SECRET_ACCESS_KEY = '{{ pillar["aws"]["secret_access_key"] }}'
AWS_STORAGE_BUCKET_NAME = '{{ pillar["aws"]["storage_bucket_name"] }}'

# Email:
DEFAULT_FROM_EMAIL = '{{ pillar["email"]["user"] }}'
EMAIL_HOST_USER = '{{ pillar["email"]["user"] }}'
EMAIL_HOST_PASSWORD = '{{ pillar["email"]["password"] }}'
EMAIL_HOST = '{{ pillar["email"]["host"] }}'
EMAIL_PORT = '{{ pillar["email"]["port"] }}'
EMAIL_USE_TLS = True
