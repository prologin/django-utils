# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from social_core.backends.open_id_connect import OpenIdConnectAuth


class ProloginSiteOpenIdConnect(OpenIdConnectAuth):
    name = "prologin-site"
    OIDC_ENDPOINT = "https://prologin.org/openid"


class ProloginSsoStaffOpenIdConnect(OpenIdConnectAuth):
    name = "prologin-sso-staff"
    OIDC_ENDPOINT = "https://sso.prologin.org/auth/realms/staff"


class ProloginSsoPieOpenIdConnect(OpenIdConnectAuth):
    name = "prologin-sso-pie"
    OIDC_ENDPOINT = "https://sso.prologin.org/auth/realms/pie"
