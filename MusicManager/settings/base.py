import os
import json

from unipath import Path
from django.core.exceptions import ImproperlyConfigured

SECRET_KEY = os.environ.get("SECRET_KEY")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).ancestor(3)

ALLOWED_HOSTS = "*"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'manager_core.apps.ManagerCoreConfig',
    'mm_user.apps.MmUserConfig',
    'crispy_forms',
    'django_cleanup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MusicManager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MusicManager.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Media files

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Set 'django-crispy-forms' template pack.
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Using custom user model.
AUTH_USER_MODEL = 'mm_user.MmUser'

# Settings related with login and logout.
LOGIN_URL = '/user/login/'
LOGOUT_URL = '/user/logout/'

LOGIN_REDIRECT_URL = '/user/main/'
LOGOUT_REDIRECT_URL = LOGIN_URL

# Settings related with sending email.

# EMAIL_HOST = str(os.environ.get("EMAIL_HOST"))
# EMAIL_PORT = int(os.environ.get("EMAIL_PORT"))
# EMAIL_HOST_USER = str(os.environ.get("EMAIL_HOST_USER"))
# EMAIL_HOST_PASSWORD = str(os.environ.get("EMAIL_HOST_PASSWORD"))
# DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
# EMAIL_USE_SSL = True

# The people who will get code error notifications. (When DEBUG=False)

ADMINS = [('Yungon', 'hahafree12@gmail.com')]
SERVER_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
