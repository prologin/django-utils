# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.contrib.auth.models import Group
from django.db import transaction

from .backend import ProloginSsoPieOpenIdConnect, ProloginSsoStaffOpenIdConnect


# pylint: disable=keyword-arg-before-vararg
def save_all_claims_as_extra_data(response, storage, social=None, *_args, **_kwargs):
    """Update user extra-data using data from provider."""
    if not social:
        return

    social.extra_data = response
    storage.user.changed(social)

    return {}


# pylint: disable=keyword-arg-before-vararg
def set_permissions(backend, response, social, user=None, *_args, **_kwargs):
    """Update user groups using data from provider."""
    if not social:
        return {}
    if backend.name not in (
        ProloginSsoStaffOpenIdConnect.name,
        ProloginSsoPieOpenIdConnect.name,
    ):
        return {}
    if not user:
        return {}

    try:
        if "superuser" in response.get("roles", []):
            user.is_superuser = True
        if "staff" in response.get("roles", []):
            user.is_staff = True
        user.save()
    except Exception as e:
        raise ValueError from e

    return {}
