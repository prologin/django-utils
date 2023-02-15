# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

import logging

from django.contrib.auth.models import Group
from django.db import transaction
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import import_from_settings

_logger = logging.getLogger(__name__)


class ProloginOIDCAB(OIDCAuthenticationBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.GroupModel = Group

    def get_username(self, claims):
        if "preferred_username" in claims:
            return claims.get("preferred_username")
        return claims.get("sub")

    def get_name(self, claims):
        if "name" in claims:
            return claims.get("name")
        return self.get_username(claims)

    def create_user(self, claims):
        email = claims.get("email")
        username = self.get_username(claims)

        _logger.debug("Creating user %s", username)
        OIDC_SYNC_GIVEN_NAME = import_from_settings(
            "OIDC_SYNC_GIVEN_NAME", False
        )

        if OIDC_SYNC_GIVEN_NAME:
            name = self.get_name(claims)
            user = self.UserModel.objects.create_user(
                username, email=email, first_name=name
            )
        else:
            user = self.UserModel.objects.create_user(username, email=email)

        self.update_groups(user, claims)

        self.set_permissions(user, claims)

        return user

    def update_user(self, user, claims):
        username = self.get_username(claims)

        OIDC_SYNC_GIVEN_NAME = import_from_settings(
            "OIDC_SYNC_GIVEN_NAME", False
        )
        if OIDC_SYNC_GIVEN_NAME:
            name = self.get_name(claims)

        _logger.debug("Updating user %s", username)

        user.username = username
        if OIDC_SYNC_GIVEN_NAME:
            user.first_name = name

        self.set_permissions(user, claims, save=False)

        user.save()

        self.update_groups(user, claims)

        return user

    def update_groups(self, user, claims):
        groups = claims.get("groups")
        user_groups = []

        for group in groups:
            user_group, _ = self.GroupModel.objects.get_or_create(name=group)
            user_groups.append(user_group)
        with transaction.atomic():
            user.groups.clear()
            user.groups.add(*set(user_groups))

    def set_permissions(self, user, claims, save=True):
        roles = claims.get("roles")
        user.is_superuser = "superuser" in roles
        user.is_staff = "staff" in roles
        if save:
            user.save()
