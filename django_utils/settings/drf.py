# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>


def rest_framework(
    throttle_rate_anon: int = 100,
    throttle_rate_user: int = 1000,
    with_auth: bool = False,
):
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "knox.auth.TokenAuthentication",
            "rest_framework.authentication.BasicAuthentication",
        ),
        "DEFAULT_THROTTLE_CLASSES": (
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ),
        "DEFAULT_THROTTLE_RATES": {
            "anon": f"{throttle_rate_anon}/hour",
            "user": f"{throttle_rate_user}/hour",
        },
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

    if with_auth:
        REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
            "mozilla_django_oidc.contrib.drf.OIDCAuthentication",
        ) + REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]

    return REST_FRAMEWORK


# Disable basic tokens
REST_AUTH_TOKEN_MODEL = None

REST_KNOX = {
    "USER_SERIALIZER": "django_utils.drf.serializers.UserSerializer",
}

SPECTACULAR_SETTINGS = {
    "ENABLE_DJANGO_DEPLOY_CHECK": False,
    "SERVE_PUBLIC": True,
    # offline support
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}
