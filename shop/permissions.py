from rest_framework import permissions


class IsAdminGroupOrReadOnly(permissions.BasePermission):
    """GET — всем, POST/PUT/PATCH/DELETE — только группа Администратор или is_staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff
            or request.user.is_superuser
            or request.user.groups.filter(name='Администратор').exists()
        )
