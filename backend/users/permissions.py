from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        if view.action == 'me':
            return (
                request.user.is_authenticated
                and request.method in permissions.SAFE_METHODS
            )

        return request.method in permissions.SAFE_METHODS
