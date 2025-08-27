from rest_framework.pagination import  PageNumberPagination
from apps.common.responses import StandardResponse

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return StandardResponse.success(
            data={
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'page_size': self.page_size,
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                }
            },
            message="Datos obtenidos exitosamente"
        )

class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
