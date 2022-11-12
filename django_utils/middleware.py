# SPDX-License-Identifier:  AGPL-3.0-only
# Copyright (c) 2020 Marin Hannache <mareo@cri.epita.fr>
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


import ipaddress

from django.conf import settings
from django.db import Error as DBError
from django.db import connections
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class XRealIPMiddleware(MiddlewareMixin):
    REAL_IP_HEADER = "HTTP_X_REAL_IP"

    def process_request(self, request):
        try:
            real_ip = ipaddress.ip_address(
                request.META.get(self.REAL_IP_HEADER)
            )
        except ValueError:
            return
        request.META["REMOTE_ADDR"] = str(real_ip)


class ProbesMiddleware(MiddlewareMixin):
    paths = {"/readiness": "readiness", "/healthz": "healthz"}

    def is_method_allowed(self, request):
        return request.method == "GET"

    def is_ip_allowed(self, request):
        ip = ipaddress.ip_address(request.META.get("REMOTE_ADDR"))
        for network in map(ipaddress.ip_network, settings.PROBES_IPS):
            if ip in network:
                return True
        return False

    def process_request(self, request):
        if not self.is_method_allowed(request) or not self.is_ip_allowed(
            request
        ):
            return None

        handler = self.paths.get(request.path, "_default_handler")
        return getattr(self, handler)(request)

    def _default_handler(self, _request):
        return None

    def readiness(self, request):
        for db_alias in connections.databases:
            if not self.check_database(db_alias):
                return HttpResponse(
                    f"error: unable to query database: {db_alias}", status=503
                )
        return self.healthz(request)

    def healthz(self, _request):
        return HttpResponse("ok")

    def check_database(self, db_alias):
        db_settings = connections.databases.get(db_alias, {})
        try:
            if db_settings.get("ENGINE", "").startswith("django.db.backends."):
                connections[db_alias].cursor().execute("SELECT 1")
        except DBError:
            return False
        return True
