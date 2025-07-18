from rest_framework import permissions


class IsStaffOrOwnerOrPublished(permissions.BasePermission):
    """
    Доступ к видео:
    - staff: доступ ко всем
    - владелец: к своему
    - остальные: если is_published=True
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.owner == request.user:
            return True
        return obj.is_published
