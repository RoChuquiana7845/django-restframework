from django.db.models.expressions import result
from rest_framework.response import  Response
from rest_framework import status
from datetime import datetime

class StandardResponse:
    @staticmethod
    def success(data=None, message="Operación exitosa", status_code=status.HTTP_200_OK, extra=None):
        response_data = {
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code,
        }

        if data is not None:
            response_data['data'] = data

        if extra:
            response_data.update(extra)

        return Response(response_data, status=status_code)

    @staticmethod
    def error(message="Error en la operación", errors=None, status_code=status.HTTP_400_BAD_REQUEST, extra=None):
        response_data = {
            'success': False,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status_code': status_code,
        }

        if errors:
            response_data['errors'] = errors

        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(data, paginator, message="Datos obtenidos exitosamente"):
        return StandardResponse.success(
            data={
                "results": data,
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "page_size": paginator.page_size,
                    "current_page": paginator.page.number,
                    "total_pages": paginator.page.paginator.num_pages,
                    "has_next": paginator.page.has_next(),
                    "has_previous": paginator.page.has_previous(),
                    "next_page": paginator.page.next_page_number() if paginator.page.has_next() else None,
                    "previous_page": paginator.page.previous_page_number() if paginator.page.has_next() else None,
                },
            },
            message=message,
        )
