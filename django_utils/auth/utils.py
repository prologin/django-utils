# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

import requests


def get_oidc_config(url: str, timeout: int = 10):
    response = requests.get(
        url,
        allow_redirects=True,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
