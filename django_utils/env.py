# SPDX-License-Identifier:  AGPL-3.0-only
# Copyright (c) 2020 Marin Hannache <mareo@cri.epita.fr>
# Copyright (c) 2020 Arthur Outhenin-Chalandre <arthur@cri.epita.fr>
# Copyright (c) 2020 Marc 'risson' Schmitt <risson@cri.epita.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from os import environ


class MissingEnvVariable(RuntimeError):
    def __init__(self, name):
        super().__init__(f"`{name}` should be present in the environment.")


FALSE_VALUES = ("0", "off", "false", "no", "")
NO_DEFAULT = object()
MISSING_ENV = object()


def ignore_missing():
    return environ.get("IGNORE_MISSING_VALUES", "") not in FALSE_VALUES


def _get_raw_value(name, default=NO_DEFAULT):
    alt_name = f"{name}_FILE"
    if (
        name not in environ
        and alt_name not in environ
        and default is NO_DEFAULT
    ):
        if ignore_missing():
            return MISSING_ENV
        raise MissingEnvVariable(name)
    if name in environ:
        return environ.get(name)
    if alt_name in environ:
        with open(environ.get(alt_name), "r") as f:
            return f.read()
    return default


def get_bool(name, default=NO_DEFAULT):
    value = _get_raw_value(name, default)
    if value is MISSING_ENV:
        return None
    if value == default:
        return value
    return value.lower() not in FALSE_VALUES


def get_string(name, default=NO_DEFAULT):
    value = _get_raw_value(name, default)
    if value is MISSING_ENV:
        return "dummy"
    return value


def get_int(name, default=NO_DEFAULT):
    value = _get_raw_value(name, default)
    if value is MISSING_ENV:
        return int()
    return int(value)


def get_list(name, default=NO_DEFAULT, separator=None):
    value = _get_raw_value(name, default)
    if value is MISSING_ENV:
        return []
    if value == default:
        return value
    return value.split(separator)


def get_secret(name, default=NO_DEFAULT, strip_value=True):
    value = get_string(name, default)
    if strip_value:
        value = value.strip()
    return value
