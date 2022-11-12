# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.conf import settings
from django.contrib import admin
from django.urls import include, path


def urlpatterns():
    urls = [
        path("admin/", admin.site.urls),
        path("", include("django_prometheus.urls")),
    ]

    if settings.DEBUG:
        urls = [path("__debug__/", include("debug_toolbar.urls"))] + urls

    return urls
