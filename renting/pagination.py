from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Clase personalizada para manejar la paginación.
    Permite al cliente usar ?page_size=X para cambiar la cantidad de resultados.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100