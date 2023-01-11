# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django_utils import env

from .debug import DEBUG

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get_secret("DJANGO_SECRET_KEY")

PROBES_IPS = env.get_list("DJANGO_PROBES_IP", ["0.0.0.0/0"])
ALLOWED_HOSTS = env.get_list("DJANGO_ALLOWED_HOSTS", [])
DEFAULT_DOMAIN = ALLOWED_HOSTS[0] if ALLOWED_HOSTS else "app.localhost"

# A list of the emails who get error notifications.
ADMINS = [(mail, mail) for mail in env.get_list("DJANGO_ADMINS", [])]
MANAGERS = [
    (mail, mail) for mail in env.get_list("DJANGO_MANAGERS", [])
] or ADMINS

# Redirect plain HTTP requests to HTTPS.
SECURE_SSL_REDIRECT = not DEBUG

# Avoid transmitting the CSRF cookie over HTTP accidentally.
CSRF_COOKIE_SECURE = not DEBUG

# Avoid transmitting the session cookie over HTTP accidentally.
SESSION_COOKIE_SECURE = not DEBUG

# See https://docs.djangoproject.com/en/4.0/ref/middleware/#referrer-policy
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


def installed_apps(with_auth: bool = False, with_pprof: bool = False):
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.humanize",
        "collectfast",  # Must be loaded before staticfiles
        "django.contrib.staticfiles",
        "django_prometheus",
        "django_celery_beat",
        "post_office",
        "drf_spectacular",
        "drf_spectacular_sidecar",
        "rest_framework",
        "knox",
    ]

    if with_auth:
        INSTALLED_APPS += [
            "mozilla_django_oidc",
        ]

    if DEBUG:
        INSTALLED_APPS += [
            "debug_toolbar",
        ]

    if with_pprof:
        INSTALLED_APPS += [
            "django_pypprof",
        ]

    return INSTALLED_APPS


def middleware(with_auth: bool = False):
    MIDDLEWARE = [
        "django_utils.middleware.XRealIPMiddleware",
        "django_utils.middleware.ProbesMiddleware",
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
    ]

    if DEBUG:
        MIDDLEWARE += [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]

    MIDDLEWARE += [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.common.BrokenLinkEmailsMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    if with_auth:
        MIDDLEWARE += [
            # "mozilla_django_oidc.middleware.SessionRefresh",
        ]

    MIDDLEWARE += [
        "django_prometheus.middleware.PrometheusAfterMiddleware",
        "django_structlog.middlewares.RequestMiddleware",
        "django_structlog.middlewares.CeleryMiddleware",
    ]

    return MIDDLEWARE


def root_urlconf(project_name: str):
    return f"{project_name}.urls"


def wsgi_application(project_name: str):
    return f"{project_name}.wsgi.application"


# Auth

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email settings

DEFAULT_FROM_EMAIL = env.get_string(
    "DJANGO_DEFAULT_FROM_EMAIL", f"noreply@{DEFAULT_DOMAIN}"
)

EMAIL_BACKEND = "post_office.EmailBackend"
POST_OFFICE = {
    "CELERY_ENABLED": True,
    "DEFAULT_PRIORITY": "now",
    "MESSAGE_ID_ENABLED": True,
    "MESSAGE_ID_FQDN": DEFAULT_DOMAIN,
    "MAX_RETRIES": 3,
    "LOG_LEVEL": 1 if not DEBUG else 2,
}
if DEBUG:
    POST_OFFICE["BACKENDS"] = {
        "default": "django.core.mail.backends.console.EmailBackend",
    }
else:
    POST_OFFICE["BACKENDS"] = {
        "default": "django.core.mail.backends.smtp.EmailBackend",
    }
    EMAIL_HOST = env.get_string("DJANGO_SMTP_HOSTNAME", "localhost")
    EMAIL_PORT = env.get_string("DJANGO_SMTP_PORT", 25)
    EMAIL_HOST_USER = env.get_string("DJANGO_SMTP_USER", "")
    EMAIL_HOST_PASSWORD = env.get_secret("DJANGO_SMTP_PASSWORD", "")
    EMAIL_USE_TLS = env.get_bool("DJANGO_SMTP_STARTTLS", False)

# Those are only used to send emails to admins and managers
SERVER_EMAIL = env.get_string("DJANGO_SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env.get_string(
    "DJANGO_EMAIL_SUBJECT_PREFIX", "[DJANGO] "
)


# Django debug toolbar

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "django_utils.settings.debug.show_toolbar",
    "SHOW_COLLAPSED": True,
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

COLLECTFAST_DEBUG = DEBUG

COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"

STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = env.get_secret("S3_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = env.get_secret("S3_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = env.get_string("S3_BUCKET")
AWS_S3_ENDPOINT_URL = env.get_string("S3_ENDPOINT")
AWS_S3_CUSTOM_DOMAIN = env.get_string("S3_CUSTOM_DOMAIN", "") or None
AWS_S3_URL_PROTOCOL = (
    "https:" if env.get_bool("S3_SECURE_URLS", True) else "http:"
)

AWS_S3_BASE_URL = (f"{AWS_S3_URL_PROTOCOL}//") + (
    AWS_S3_CUSTOM_DOMAIN or f"localhost:8020/{AWS_STORAGE_BUCKET_NAME}"
)

AWS_STATIC_LOCATION = "static"
STATIC_URL = f"{AWS_S3_BASE_URL}/{AWS_STATIC_LOCATION}/"
STATICFILES_STORAGE = "django_utils.storage.backends.StaticStorage"

AWS_PUBLIC_MEDIA_LOCATION = "media/public"
MEDIA_URL = f"{AWS_S3_BASE_URL}/{AWS_PUBLIC_MEDIA_LOCATION}/"
DEFAULT_FILE_STORAGE = "django_utils.storage.backends.PublicMediaStorage"

AWS_PRIVATE_MEDIA_LOCATION = "media/private"
PRIVATE_FILE_STORAGE = "django_utils.storage.backends.PrivateMediaStorage"
