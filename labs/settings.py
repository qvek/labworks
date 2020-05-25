"""
Django settings for labs project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

AUTH_USER_MODEL = 'labworks.LabworksUser'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


DEFAULT_FROM_EMAIL = 'labworks@mpt.ru'
SERVER_EMAIL = 'labworks@mpt.ru'
ADMINS = (('Dmitriy', 'd.s.harchenko@mpt.ru'),)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!%0@pd-9vcgp20n%_sh)2ppwld=p+h*8388@*k-j-xs7&7ryf&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += ("django.core.context_processors.request",)

ALLOWED_HOSTS = ['labworks.mpt.ru', 'lw.mpt.ru']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'labs.labworks'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'labs.urls'

WSGI_APPLICATION = 'labs.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

#if DEBUG: DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'labworks',
#        'USER':'root',
#        'PASSWORD':'root',
#        'HOST':'db'
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'labworks',
        'USER':'labworksUser',
        'PASSWORD':'DJvXHJG6q7EC5rdN',
        'HOST':'localhost'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'ru-RU' #en-us

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = '/home/user/labworks/static'
STATIC_URL = '/static/'

MEDIA_ROOT = '/home/user/labworks/uploadfiles'
MEDIA_URL = '/files/'

EXCEL_ROOT = '/home/user/labworks/excel' #Excel reports
