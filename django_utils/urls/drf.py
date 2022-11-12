# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from ..drf.views import WhoAmIView


def urlpatterns(with_auth: bool = False):
    urls = [
        # Auth
        path("rest/auth/", include("knox.urls")),
        path(
            "rest/auth/user/",
            WhoAmIView.as_view(),
            name="rest-auth-user-details",
        ),
        # API docs
        path("rest/doc/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "rest/doc/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="schema-swagger",
        ),
        path(
            "rest/doc/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="schema-redoc",
        ),
    ]

    if with_auth:
        urls += [
            path("rest/auth/oidc/", include("mozilla_django_oidc.urls")),
        ]

    return urls
