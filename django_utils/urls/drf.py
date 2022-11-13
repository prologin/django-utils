# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django_utils.drf.views import WhoAmIView


def urlpatterns(apps_with_api=None, with_auth: bool = False):
    if apps_with_api is None:
        apps_with_api = []


    @api_view(["GET"])
    def api_root(request, format=None):
        data = {}
        for app in apps_with_api:
            data[app] = reverse(
                f"{app}-api-root", request=request, format=format
            )
        return Response(data)


    urls = [
        path("rest/", api_root),
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
    ] + [path(f"api/{app}/", include(f"{app}.urls")) for app in apps_with_api]

    if with_auth:
        urls += [
            path("rest/auth/oidc/", include("mozilla_django_oidc.urls")),
        ]

    return urls
