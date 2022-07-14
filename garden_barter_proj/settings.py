from pathlib import Path
from corsheaders.defaults import default_headers
import decouple
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = decouple.config('DJANGO_DEBUG')

# set SECRET_KEY based on value of DEBUG
if DEBUG:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = decouple.config('DJANGO_SECRET_KEY_DEVELOPMENT')
else:
    SECRET_KEY = decouple.config('DJANGO_SECRET_KEY_PRODUCTION')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',

    'pages_app',
    'users_app',
    'barters_app',
    'messages_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'garden_barter_proj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR/'templates')],
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

WSGI_APPLICATION = 'garden_barter_proj.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Fixtures
FIXTURES_DIRS = [BASE_DIR/'fixtures']

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [str(BASE_DIR/'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users_app.User'


# define default authentication method in DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),

    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer', ),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken', ),
}

# The blacklist app also provides a management command, 
# flushexpiredtokens, which will delete any tokens from 
# the outstanding list and blacklist that have expired. 
# You should set up a cron job on your server or hosting 
# platform which runs this command daily.


# CSRF_USE_SESSIONS = False

# define refresh token lifetime
REFRESH_TOKEN_EXPIRY = {
    'days': 7,
    'hours': 0,
    'minutes': 0,
    'seconds': 0
}

# define refresh token lifetime
ACCESS_TOKEN_EXPIRY = {
    'days': 0,
    'hours': 10,
    'minutes': 0,
    'seconds': 10
}

REFRESH_TOKEN_SECRET = decouple.config('DJANGO_REFRESH_TOKEN_SECRET')
ACCESS_TOKEN_SECRET = decouple.config('DJANGO_ACCESS_TOKEN_SECRET')

# to accept cookies via axios
CORS_ALLOW_CREDENTIALS = True

# CSRF_HEADER_NAME = 'X-CSRFToken'

# CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SAMESITE='None'
# CSRF_COOKIE_SECURE = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    # other allowed origins...
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    # other allowed origins...
]

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    # other allowed hosts...
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'refresh_token',
    'withcredentials',
    'access-control-allow-origin',
]

