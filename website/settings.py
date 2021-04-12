"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
import environ
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load sensitive variables from ../.env
# .env should contain the following:
# DJANGO_DEBUG - FALSE enables production configuration
# SECRET_KEY - ONLY for production
# DATABASE_NAME - ONLY for production
# DATABASE_USERNAME - ONLY for production
# DATABASE_PASSWORD - ONLY for production
# DATABASE_HOST - ONLY for production
# DATABASE_PORT - ONLY for production
# STATIC_ROOT - ONLY for production
# MEDIA_ROOT - ONLY for production
# SECURE_MEDIA_ROOT - ONLY for production

env = environ.Env()
environ.Env.read_env("../.env")

# configuration considering development and production
if env('DJANGO_DEBUG') == 'FALSE':
    # apply settings needed for the production server
    DEBUG = False
    ALLOWED_HOSTS = ['*']

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    # seems to generate a lot of trouble
    # SECURE_SSL_REDIRECT = True

    SECRET_KEY = env("SECRET_KEY")

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DATABASE_NAME'),
            'USER': env('DATABASE_USERNAME'),
            'PASSWORD': env('DATABASE_PASSWORD'),
            'HOST': env('DATABASE_HOST'),
            'PORT': env('DATABASE_PORT'),
        }
    }

    # paths for STATIC, MEDIA and SECURE_MEDIA
    STATIC_ROOT = env('STATIC_ROOT')
    MEDIA_ROOT = env('MEDIA_ROOT')
    SECURE_MEDIA_ROOT = env('SECURE_MEDIA_ROOT')


elif env('DJANGO_DEBUG') == 'FALSE_HTTP':
    # apply settings needed for the testing server
    DEBUG = False
    ALLOWED_HOSTS = ['*']

    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_BROWSER_XSS_FILTER = False

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'ard4+6zo@23rdb%hq@tlcdmtc&p5j4w+p7isknx3p0fojx0k%='

    # to keep the installation simple we are not using PostgreSQL for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database.db',
        }
    }

    # paths for STATIC, MEDIA and SECURE_MEDIA
    STATIC_ROOT = env('STATIC_ROOT')
    MEDIA_ROOT = env('MEDIA_ROOT')
    SECURE_MEDIA_ROOT = env('SECURE_MEDIA_ROOT')


else:
    # apply settings needed for the development process

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/
    DEBUG = True

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'ard4+6zo@23rdb%hq@tlcdmtc&p5j4w+p7isknx3p0fojx0k%='

    # to keep the installation simple we are not using PostgreSQL for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database.db',
        }
    }

    # paths for STATIC, MEDIA and SECURE_MEDIA
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')
    SECURE_MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'securemedia')


# settings for STATIC, MEDIA and SECURE_MEDIA
STATIC_URL = '/static/'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR]
MEDIA_URL = '/media/'
# url to be called -> django handles user authentication
SECURE_MEDIA_URL = '/securemedia/'
SECURE_MEDIA_STORAGE = FileSystemStorage(location=SECURE_MEDIA_ROOT, base_url=SECURE_MEDIA_URL)

# Application definition

INSTALLED_APPS = [
    'authentication',
    'homepage',
    'psucontrol',
    'psufrontend',
    'mailer',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "website", "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'extra_utils': 'website.templatetags.extra_utils',
            }
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

# authentication settings
AUTH_USER_MODEL = 'authentication.User'
LOGIN_URL = 'auth:login'

# model/database settings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# e-mail settings
EMAIL_BACKEND = "mailer.backend.DbBackend"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/


LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True
