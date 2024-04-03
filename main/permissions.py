"""Custom permissions"""

from rest_framework import permissions


class UserIsOwnerPermission(permissions.BasePermission):
    """Determines if the user owns the object"""

    def has_object_permission(self, request, view, obj):
        """
        Returns True if the requesting user is the owner of the object as
        determined by the "owner_field" property on the view. If no "owner_field"
        is given, the object itself is assumed to be the User object.
        """
        owner_field = getattr(view, "owner_field", None)

        if owner_field is None:
            # if no owner_field is specified, the object itself is compared
            owner = obj
        else:
            # otherwise we lookup the owner by the specified field
            owner = getattr(obj, owner_field)

        return owner == request.user


class UserIsOwnerOrAdminPermission(UserIsOwnerPermission):
    """Determines if the user owns the object or is a staff user"""

    def has_object_permission(self, request, view, obj):
        """
        Returns True if the requesting user is admin or the owner of the object as
        determined by the "owner_field" property on the view. If no "owner_field"
        is given, the object itself is assumed to be the User object.
        """
        if request.user and (request.user.is_staff or request.user.is_superuser):
            return True
        return super().has_object_permission(request, view, obj)
