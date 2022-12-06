# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django.conf import settings
from django.contrib import admin
from django.urls import include, path


def urlpatterns(with_pprof: bool = False):
    urls = [
        path("admin/", admin.site.urls),
        path("", include("django_prometheus.urls")),
    ]

    if with_pprof:
        urls += [
            path("debug/pprof/", include("django_pypprof.urls")),
        ]

    if settings.DEBUG:
        urls = [path("__debug__/", include("debug_toolbar.urls"))] + urls

    return urls
