import os
from dotenv import load_dotenv
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

from dj_core_utils.settings.cors import get_cors_settings # noqa
from dj_core_utils.settings.base import CoreSettings # noqa


class BaseSetting(CoreSettings):
    # Database settings
    DATABASES = {
        'default': {
            **CoreSettings.DATABASES['default'],
            'OPTIONS': {'options': '-c search_path=business,public'}
        }
    }

    # Installed apps
    INSTALLED_APPS = CoreSettings.INSTALLED_APPS + [
        'django.contrib.admin',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'dj_users'
    ]

    # Middleware
    MIDDLEWARE = CoreSettings.MIDDLEWARE + [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    ]

    # JWT
    SIMPLE_JWT = {
        **CoreSettings.SIMPLE_JWT,
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),
    }

    # Otros settings
    ROOT_URLCONF = 'demo.urls'
    WSGI_APPLICATION = "demo.wsgi.application"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},  # noqa
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},  # noqa
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},  # noqa
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},  # noqa
    ]

    LANGUAGE_CODE = "es-mx"
    LANGUAGES = [
        ('en', 'English'),
        ('es', 'Español'),
    ]
    USE_I18N = True
    TIME_ZONE = "UTC"
    USE_TZ = True

    STATIC_URL = "static/"
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # CORS
    try:
        CORS_ALLOWED_ORIGINS = get_cors_settings('diiwo_backend')['CORS_ALLOWED_ORIGINS']  # noqa
    except Exception as e:
        print(f"Error loading CORS settings: {e}")

    ALLOWED_HOSTS = CoreSettings.ALLOWED_HOSTS


for setting_name in dir(BaseSetting):
    if setting_name.isupper():
        setting_value = getattr(BaseSetting, setting_name)
        globals()[setting_name] = setting_value
