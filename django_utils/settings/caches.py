# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django_utils import env


def caches_default():
    return {
        "BACKEND": "django_prometheus.cache.backends.redis.RedisCache",
        "LOCATION": env.get_string(
            "DJANGO_CACHE_URL", "redis://localhost:6379/0"
        ),
    }


def caches():
    return {
        "default": caches_default(),
    }


CACHES = caches()


USE_CACHE_AS_SESSION_ENGINE = env.get_bool(
    "DJANGO_USE_CACHE_AS_SESSION_ENGINE", False
)
if USE_CACHE_AS_SESSION_ENGINE:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
