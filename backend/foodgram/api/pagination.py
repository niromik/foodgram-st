from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация для API-эндпоинтов."""

    page_size = 10
    page_size_query_param = 'limit'
