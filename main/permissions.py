from rest_framework import permissions


class CustomAdminPermission(permissions.BasePermission):
    """
    - Normal user with `can_create_project`: can create + view.
    - Normal user without permission: read-only.
    - Admin (staff/superuser): full access.
    """

    def has_permission(self, request, view):
        user = request.user

        # Everyone can list/retrieve (view)
        if view.action in ["list", "retrieve"]:
            return True

        # Admins can do everything
        if user.is_staff or user.is_superuser:
            return True

        # Check if user has the custom permission
        if view.action == "create" and user.has_perm("main.can_create_project"):
            return True

        # All other actions (update, delete, approve) → admin only
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class AttendancePermission(permissions.BasePermission):
    """
    - Authenticated users can create and view their own attendance records.
    - Admins or users with 'can_manage_attendance' can view/manage all.
    - Only admin/can_manage_attendance can update/delete others' records.
    """
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.has_perm('main.can_manage_attendance'):
            return True
        if view.action in ['list', 'retrieve', 'create']:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.has_perm('main.can_manage_attendance'):
            return True
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return obj.user == request.user
        return False


class MessagePermission(permissions.BasePermission):
    """
    - Users can view only their own messages (as sender or receiver).
    - Only admin can update/delete any message.
    - No one can create via API except admin (messages are system-generated or via other logic).
    """
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        if view.action in ['list', 'retrieve']:
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if view.action in ['retrieve']:
            return obj.sender == request.user or obj.receiver == request.user
        return False

