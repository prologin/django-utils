# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

_logger = logging.getLogger(__name__)


class ProloginOIDCAB(OIDCAuthenticationBackend):
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

        name = self.get_name(claims)
        return self.UserModel.objects.create_user(
            username, email=email, first_name=name
        )

    def update_user(self, user, claims):
        username = self.get_username(claims)
        name = self.get_name(claims)

        _logger.debug("Updating user %s", username)

        user.username = username
        user.first_name = name

        user.save()
        return user
