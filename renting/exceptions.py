from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Llama al manejador estándar primero
    response = exception_handler(exc, context)

    # Si la respuesta es None, es un error que Django no atrapó (ej. error 500)
    if response is None:
        return Response({
            'error': 'Server Error',
            'message': 'Error interno en el servidor del Equipo 5.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Para unificar el formato de todos los errores (400, 401, 404, etc.)
    return Response({
        'error': 'Client Error',
        'status_code': response.status_code,
        'details': response.data
    }, status=response.status_code)