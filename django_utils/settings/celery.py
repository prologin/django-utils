# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django_utils import env

CELERY_BROKER_URL = env.get_string("CELERY_BROKER_URL", None)
CELERY_RESULT_BACKEND = env.get_string(
    "CELERY_RESULT_BACKEND", CELERY_BROKER_URL
)
CELERY_RESULT_EXPIRES = env.get_int(
    "CELERY_RESULT_EXPIRES", 12 * 60 * 60
)  # in seconds
