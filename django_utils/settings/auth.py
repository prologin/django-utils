# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.urls import reverse_lazy

from django_utils import env
from django_utils.auth.utils import get_oidc_config

OIDC_DRF_AUTH_BACKEND = "django_utils.auth.backend.ProloginOIDCAB"

AUTHENTICATION_BACKENDS = [
    OIDC_DRF_AUTH_BACKEND,
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = reverse_lazy("oidc_authentication_init")
LOGOUT_URL = reverse_lazy("oidc_logout")

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_ERROR_URL = "/"


# OIDC

OIDC_OP_CONFIG_URL = (
    env.get_string("PROLOGIN_OIDC_URL") + "/.well-known/openid-configuration"
)
OIDC_TIMEOUT = env.get_int("PROLOGIN_OIDC_TIMEOUT", 15)

OIDC_RP_SCOPES = " ".join(["openid", "email", "profile", "roles"])
OIDC_OP_CONFIG = get_oidc_config(OIDC_OP_CONFIG_URL, timeout=OIDC_TIMEOUT)
OIDC_OP_AUTHORIZATION_ENDPOINT = OIDC_OP_CONFIG["authorization_endpoint"]
OIDC_OP_TOKEN_ENDPOINT = OIDC_OP_CONFIG["token_endpoint"]
OIDC_OP_USER_ENDPOINT = OIDC_OP_CONFIG["userinfo_endpoint"]
OIDC_OP_LOGOUT_URL_METHOD = OIDC_OP_CONFIG["end_session_endpoint"]
OIDC_RP_CLIENT_ID = env.get_secret("PROLOGIN_OIDC_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env.get_secret("PROLOGIN_OIDC_CLIENT_SECRET")
OIDC_RP_SIGN_ALGO = env.get_string("OIDC_RP_SIGN_ALGO", "RS256")

if OIDC_RP_SIGN_ALGO == "RS256":
    OIDC_OP_JWKS_ENDPOINT = OIDC_OP_CONFIG["jwks_uri"]
