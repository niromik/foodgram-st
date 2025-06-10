from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorized(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated
