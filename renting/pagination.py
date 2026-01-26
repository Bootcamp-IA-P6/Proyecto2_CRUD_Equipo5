from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class supporting dynamic page size.
    Allows ?page_size=X parameter to control results per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
