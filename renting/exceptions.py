from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent API error responses.
    Returns unified error format for both handled and unhandled exceptions.
    """
    # Call default DRF exception handler first
    response = exception_handler(exc, context)

    # If response is None, it's an unhandled server error (real 500)
    if response is None:
        return Response({
            'error': 'Internal Server Error',
            'message': 'An error occurred on the server.',
            # Remove debug_info for production (#54 compliance)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Return unified format for handled client errors
    return Response({
        'error': 'Client Error',
        'status_code': response.status_code,
        'details': response.data
    }, status=response.status_code)
