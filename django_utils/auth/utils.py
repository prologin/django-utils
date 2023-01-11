# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

import requests
from mozilla_django_oidc.utils import import_from_settings

from django_utils import env


def get_oidc_config(url: str, timeout: int = 10):
    response = requests.get(
        url,
        allow_redirects=True,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def get_auth_headers_for_app(app_name: str):
    app_name_normalized = app_name.upper().replace("-", "_")

    OIDC_OP_CONFIG_URL = env.get_string(
        f"OIDC_{app_name_normalized}_OP_CONFIG_URL", None
    )

    if OIDC_OP_CONFIG_URL is not None:
        OIDC_OP_CONFIG_URL += "/.well-known/openid-configuration"
    else:
        OIDC_OP_CONFIG_URL = import_from_settings("OIDC_OP_CONFIG_URL")

    OIDC_TIMEOUT = env.get_int(
        f"OIDC_{app_name_normalized}_TIMEOUT",
        import_from_settings("OIDC_TIMEOUT", 15),
    )

    OIDC_OP_CONFIG = get_oidc_config(OIDC_OP_CONFIG_URL, timeout=OIDC_TIMEOUT)

    OIDC_OP_TOKEN_ENDPOINT = OIDC_OP_CONFIG["token_endpoint"]

    OIDC_RP_SCOPES = " ".join(
        env.get_list(
            f"OIDC_{app_name_normalized}_RP_SCOPES",
            ["openid", "email", "profile", "roles"],
        )
    )

    OIDC_RP_CLIENT_ID = env.get_secret(
        f"OIDC_{app_name_normalized}_RP_CLIENT_ID"
    )
    OIDC_M2M_USERNAME = env.get_secret(
        f"OIDC_{app_name_normalized}_M2M_USERNAME"
    )
    OIDC_M2M_PASSWORD = env.get_secret(
        f"OIDC_{app_name_normalized}_M2M_PASSWORD"
    )

    form = {
        "grant_type": "client_credentials",
        "client_id": OIDC_RP_CLIENT_ID,
        "scope": OIDC_RP_SCOPES,
        "username": OIDC_M2M_USERNAME,
        "password": OIDC_M2M_PASSWORD,
    }

    response = requests.post(
        OIDC_OP_TOKEN_ENDPOINT,
        allow_redirects=True,
        timeout=OIDC_TIMEOUT,
        data=form,
    )

    response.raise_for_status()

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }
