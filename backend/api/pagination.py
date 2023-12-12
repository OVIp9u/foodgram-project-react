from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class CustomPaginator(PageNumberPagination):
    """Пагинация для вывода 6 элементов на странице + limit."""
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
