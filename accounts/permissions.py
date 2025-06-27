from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class IsAnonymous(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            raise PermissionDenied(
                _('You are already authenticated. Please logout first to access this page.')
            )
        return True