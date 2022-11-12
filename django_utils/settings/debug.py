# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from django_utils import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.get_bool("DJANGO_DEBUG", False)


def show_toolbar(request):
    from django.conf import settings  # pylint:disable=import-outside-toplevel

    return settings.DEBUG
