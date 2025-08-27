from rest_framework.views import exception_handler
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError
from .responses import StandardResponse
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        view = context.get('view', None)
        request = context.get('request', None)

        error_info = {
            "view": view.__class__.__name__ if view else 'Unknown',
            "method": request.method if request else 'Unknown',
            "path": request.path if request else 'Unknown',
            "User": str(request.user) if request and hasattr(request, 'user') else 'Anonymous',
            "error": str(exc),
        }
        logger.error(f"API Error: {error_info}")

        if isinstance(exc, Http404):
            return StandardResponse.error(
                message="Recurso no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        elif isinstance(exc, ValidationError):
            return StandardResponse.error(
                message="Error de validación",
                errors=response.data,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            return StandardResponse.error(
                message="Datos inválidos proporcionados",
                errors=response.data,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            return StandardResponse.error(
                message="No autorizado. Credenciales inválidas o faltantes",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            return StandardResponse.error(
                message="Prohibido. No tiene permisos para realizar esta acción",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            return StandardResponse.error(
                message="Método no permitido",
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        elif response.status_code >= 500:
            return StandardResponse.error(
                message="Error interno del servidor",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        else:
            return StandardResponse.error(
                message=str(exc),
                errors=response.data,
                status_code=response.status_code,
            )

    return response