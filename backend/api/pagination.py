from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class CustomPaginator(PageNumberPagination):
    """Пагинация для вывода 6 элементов на странице + limit."""
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
