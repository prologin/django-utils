# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

# See https://docs.djangoproject.com/en/4.0/ref/settings/#databases

from django_utils import env


def databases_default(project_name: str):
    return {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": env.get_string("DB_NAME", project_name),
        "USER": env.get_string("DB_USER", project_name),
        "PASSWORD": env.get_secret("DB_PASSWORD"),
        "HOST": env.get_string("DB_HOST", "localhost"),
        "PORT": env.get_int("DB_PORT", 5432),
    }


def databases(project_name: str):
    return {
        "default": databases_default(project_name),
    }
