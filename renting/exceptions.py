from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Primero, llamamos al manejador por defecto de REST framework
    response = exception_handler(exc, context)

    # Si response es None, significa que ha ocurrido un error que DRF no ha capturado (un Error 500 real)
    if response is None:
        return Response({
            'error': 'Server Error',
            'message': 'Error interno en el servidor del Equipo 5.',
            'debug_info': str(exc)  # Esto nos ayudará a ver el error real en los tests
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Si hay respuesta, devolvemos el formato unificado que acordamos
    return Response({
        'error': 'Client Error',
        'status_code': response.status_code,
        'details': response.data
    }, status=response.status_code)