from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Права доступа: разрешение записи только владельцам, чтение - всем.

    Безопасные методы (GET, HEAD, OPTIONS) разрешены всем пользователям.
    Методы изменения (POST, PUT, PATCH, DELETE) разрешены только:
        Аутентифицированным пользователям (на уровне объекта)
        Владельцам объекта (на уровне экземпляра)
    """

    def has_object_permission(self, request, view, obj):
        """Проверка прав доступа для конкретного объекта."""
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user

    def has_permission(self, request, view):
        """Глобальная проверка прав доступа для всего эндпоинта."""
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
