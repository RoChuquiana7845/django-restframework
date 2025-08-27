from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets.company import CompanyViewSet

router = DefaultRouter()
router.register('company', CompanyViewSet)
app_name = 'business'

urlpatterns = [
    path('', include(router.urls)),
]