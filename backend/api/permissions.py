from rest_framework import permissions


class RecipePermissions(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        user = request.user

        allowed_actions = (
            'list', 'retrieve', 'create',
        )

        author_allowed_actions = (
            'partial_update', 'destroy',
        )

        return (
            view.action in allowed_actions
            or (
                view.action in author_allowed_actions
                and obj.author == user
            )
        )
