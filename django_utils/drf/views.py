# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2022 Association Prologin <association@prologin.org>
# Copyright (c) 2022 Marc 'risson' Schmitt <marc.schmitt@prologin.org>

from knox.settings import knox_settings
from rest_framework import permissions, response, serializers, views

from .serializers import UserSerializer


class WhoAmIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    # pylint:disable=redefined-builtin,unused-argument
    def get(self, request, format=None):
        serializer = knox_settings.USER_SERIALIZER or UserSerializer
        return response.Response(
            serializer(request.user, context={"request": request}).data
        )
