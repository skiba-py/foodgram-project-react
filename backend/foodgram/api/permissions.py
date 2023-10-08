from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorStaffOrReadOnly(BasePermission):
    """Вносить изменения могут только Author и Staff."""

    def has_permission(self, request, view):
        if request.user.is_anonymous and 'me' in request.path:
            return False
            # raise PermissionDenied(
            #     detail="You must be authenticated to access this resource."
            # )
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.is_anonymous and 'me' in request.data:
            raise PermissionDenied(
                detail="You must be authenticated to access this resource."
            )
        return (
            request.method in SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(BasePermission):
    """Создание и редактирование только для Admin."""

    def has_permission(self, request, view) -> bool:
        return (
                request.method in SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_active
                and request.user.is_staff
        )


class OwnerUserOrReadOnly(BasePermission):
    """Создание и редактирование только для Owner и Admin"""

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user.is_authenticated and 'me' in request.data:
            raise PermissionDenied(
                detail="You must be authenticated to access this resource."
            )
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            and request.user.is_staff
        )
