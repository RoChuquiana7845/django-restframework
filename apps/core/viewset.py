# apps/core/viewsets.py
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone
from django.http import Http404
from apps.common.responses import StandardResponse
from apps.core.pagination import StandardResultsSetPagination
import logging

logger = logging.getLogger(__name__)


class BaseViewSetMixin:
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()

        if hasattr(queryset.model, 'is_active'):
            if not self.request.query_params.get('include_inactive'):
                queryset = queryset.filter(is_active=True)

        if hasattr(queryset.model, 'deleted_at'):
            if not self.request.query_params.get('include_deleted'):
                queryset = queryset.filter(deleted_at__isnull=True)

        return queryset

    def perform_create(self, serializer):
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()


class StandardResponseMixin:

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().create(request, *args, **kwargs)
                return StandardResponse.success(
                    data=response.data,
                    message="Registro creado exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Error creating {self.get_serializer().Meta.model.__name__}: {str(e)}")
            return StandardResponse.error(
                message="Error al crear el registro",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().update(request, *args, **kwargs)
                return StandardResponse.success(
                    data=response.data,
                    message="Registro actualizado exitosamente"
                )
        except Exception as e:
            logger.error(f"Error updating {self.get_serializer().Meta.model.__name__}: {str(e)}")
            return StandardResponse.error(
                message="Error al actualizar el registro",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if hasattr(instance, 'soft_delete'):
                instance.soft_delete(user=request.user)
                message = "Registro eliminado exitosamente"
            else:
                instance.delete()
                message = "Registro eliminado permanentemente"

            return StandardResponse.success(message=message)
        except Http404:
            return StandardResponse.error(
                message="Registro no encontrado",
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting {self.get_serializer().Meta.model.__name__}: {str(e)}")
            return StandardResponse.error(
                message="Error al eliminar el registro",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class BulkOperationsMixin:

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data, many=True)
                serializer.is_valid(raise_exception=True)
                instances = serializer.save()

                return StandardResponse.success(
                    data=serializer.data,
                    message=f"{len(instances)} registros creados exitosamente",
                    status_code=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Error in bulk_create: {str(e)}")
            return StandardResponse.error(
                message="Error en la creación en lote",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        try:
            with transaction.atomic():
                updated_count = 0
                for item in request.data:
                    if 'id' in item:
                        instance = self.get_queryset().get(id=item['id'])
                        serializer = self.get_serializer(instance, data=item, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        updated_count += 1

                return StandardResponse.success(
                    message=f"{updated_count} registros actualizados exitosamente"
                )
        except Exception as e:
            logger.error(f"Error in bulk_update: {str(e)}")
            return StandardResponse.error(
                message="Error en la actualización en lote",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        try:
            ids = request.data.get('ids', [])
            if not ids:
                return StandardResponse.error(
                    message="Debe proporcionar una lista de IDs",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                queryset = self.get_queryset().filter(id__in=ids)
                deleted_count = 0

                for instance in queryset:
                    if hasattr(instance, 'soft_delete'):
                        instance.soft_delete(user=request.user)
                    else:
                        instance.delete()
                    deleted_count += 1

                return StandardResponse.success(
                    message=f"{deleted_count} registros eliminados exitosamente"
                )
        except Exception as e:
            logger.error(f"Error in bulk_delete: {str(e)}")
            return StandardResponse.error(
                message="Error en la eliminación en lote",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class StatusToggleMixin:

    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        try:
            instance = self.get_object()
            if hasattr(instance, 'is_active'):
                instance.is_active = not instance.is_active
                instance.save()
                status_text = "activado" if instance.is_active else "desactivado"
                return StandardResponse.success(
                    message=f"Registro {status_text} exitosamente"
                )
            else:
                return StandardResponse.error(
                    message="Este modelo no soporta cambio de estado",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error in toggle_status: {str(e)}")
            return StandardResponse.error(
                message="Error al cambiar el estado",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class BaseModelViewSet(BaseViewSetMixin,
                       StandardResponseMixin,
                       BulkOperationsMixin,
                       StatusToggleMixin,
                       viewsets.ModelViewSet):
    pass


class ReadOnlyBaseViewSet(BaseViewSetMixin, viewsets.ReadOnlyModelViewSet):
    pass


class CatalogViewSet(BaseModelViewSet):
    ordering_fields = ['order', 'name', 'code']
    ordering = ['order', 'name']
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['is_active', 'code']

    @action(detail=False, methods=['get'])
    def active_list(self, request):
        try:
            queryset = self.get_queryset().filter(is_active=True)
            data = [
                {
                    'id': item.id,
                    'code': item.code,
                    'name': item.name
                }
                for item in queryset
            ]
            return StandardResponse.success(data=data)
        except Exception as e:
            logger.error(f"Error in active_list: {str(e)}")
            return StandardResponse.error(
                message="Error al obtener la lista activa",
                status_code=status.HTTP_400_BAD_REQUEST
            )

