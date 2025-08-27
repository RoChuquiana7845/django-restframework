# 🚀 Django REST Framework - Plantilla CRUD Base

Una plantilla robusta y reutilizable para crear APIs REST con Django que permite generar **CRUDs completos en minutos** usando mixins estandarizados.

## 🎯 ¿Por qué usar esta plantilla?

- ✅ **CRUD completo en 3 líneas de código**
- ✅ **Validaciones automáticas** (cédula ecuatoriana, RUC, emails)
- ✅ **Respuestas estandarizadas** en toda la API
- ✅ **Filtros y búsqueda** incluidos
- ✅ **Admin personalizado** con auditoría
- ✅ **Operaciones en lote** (bulk create, update, delete)
- ✅ **Arquitectura escalable** y mantenible

## 📋 Requisitos

- Python 3.9+
- Django 4.2+
- PostgreSQL/SQLite

## ⚡ Instalación Rápida (5 minutos)

```bash
# 1. Crear proyecto
django-admin startproject config .

# 2. Crear apps
mkdir apps && touch apps/__init__.py
cd apps
python ../manage.py startapp core
python ../manage.py startapp business
python ../manage.py startapp common
cd ..

# 3. Instalar dependencias
pip install Django==4.2.7 djangorestframework==3.14.0 django-filter==23.3 django-cors-headers==4.3.1 python-decouple==3.8 drf-yasg==1.21.7 Pillow==10.1.0

# 4. Configurar settings, copiar archivos core
# 5. Migrar y crear superusuario
python manage.py migrate
python manage.py createsuperuser

# 6. Ejecutar
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
proyecto/
├── config/                 # Configuraciones Django
│   ├── settings/
│   │   ├── base.py        # Settings principales
│   │   ├── development.py  # Para desarrollo
│   │   └── production.py   # Para producción
│   └── urls.py            # URLs principales
├── apps/
│   ├── core/              # Funcionalidades base (reutilizables)
│   │   ├── models.py      # BaseModel, CatalogModel, etc.
│   │   ├── serializers.py # BaseModelSerializer
│   │   ├── viewsets.py    # BaseModelViewSet (mixins)
│   │   └── admin.py       # BaseModelAdmin
│   ├── business/          # Tu dominio de negocio
│   │   ├── models/        # Tus modelos específicos
│   │   ├── serializers/   # Tus serializers
│   │   ├── viewsets/      # Tus viewsets
│   │   ├── admin.py       # Admin personalizado
│   │   └── urls.py        # URLs de la app
│   └── common/            # Utilidades compartidas
│       └── responses.py   # Respuestas estandarizadas
```

## 🚀 Crear un CRUD Completo (2 minutos)

### 1. Definir Modelo
```python
# apps/business/models.py
from apps.core.models import BaseModel

class Product(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
```

### 2. Crear Serializer
```python
# apps/business/serializers.py
from apps.core.serializers import BaseModelSerializer
from .models import Product

class ProductSerializer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
```

### 3. Crear ViewSet
```python
# apps/business/viewsets.py
from apps.core.viewsets import BaseModelViewSet
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = ['code', 'name']
    filterset_fields = ['is_active']
```

### 4. Registrar URLs
```python
# apps/business/urls.py
from rest_framework.routers import DefaultRouter
from .viewsets import ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
urlpatterns = router.urls
```

### 5. Configurar Admin
```python
# apps/business/admin.py
from django.contrib import admin
from apps.core.admin import BaseModelAdmin
from .models import Product

@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    list_display = ('code', 'name', 'price', 'is_active')
    search_fields = ('code', 'name')
```

**¡LISTO!** Con esto tienes:
- ✅ CRUD completo: GET, POST, PUT, PATCH, DELETE
- ✅ Filtros: `?search=producto&is_active=true`
- ✅ Paginación automática
- ✅ Admin interface
- ✅ Validaciones
- ✅ Respuestas estandarizadas
- ✅ Operaciones en lote

## 📡 Endpoints que obtienes GRATIS

### CRUD Básico
```bash
GET    /api/v1/products/           # Lista paginada
POST   /api/v1/products/           # Crear
GET    /api/v1/products/{id}/      # Detalle
PUT    /api/v1/products/{id}/      # Actualizar completo
PATCH  /api/v1/products/{id}/      # Actualizar parcial
DELETE /api/v1/products/{id}/      # Eliminar (soft delete)
```

### Funciones Extra
```bash
PATCH  /api/v1/products/{id}/toggle_status/  # Activar/desactivar
POST   /api/v1/products/bulk_create/         # Crear múltiples
PATCH  /api/v1/products/bulk_update/         # Actualizar múltiples
DELETE /api/v1/products/bulk_delete/         # Eliminar múltiples
```

### Filtros Automáticos
```bash
GET /api/v1/products/?search=laptop
GET /api/v1/products/?is_active=true
GET /api/v1/products/?ordering=name
GET /api/v1/products/?page=2&page_size=50
GET /api/v1/products/?created_date_from=2024-01-01
```

## 🎯 Ejemplos de Uso

### Crear Producto
**POST** `/api/v1/products/`
```json
{
    "code": "LAPTOP001",
    "name": "MacBook Pro 13",
    "price": 2500.00,
    "description": "Laptop profesional"
}
```

**Respuesta:**
```json
{
    "success": true,
    "message": "Registro creado exitosamente",
    "data": {
        "id": "uuid-here",
        "code": "LAPTOP001",
        "name": "MacBook Pro 13",
        "price": "2500.00",
        "is_active": true,
        "created_at": "2024-01-15 10:30:00"
    }
}
```

### Crear Múltiples
**POST** `/api/v1/products/bulk_create/`
```json
[
    {"code": "MOUSE001", "name": "Mouse Inalámbrico", "price": 25.00},
    {"code": "KEYB001", "name": "Teclado Mecánico", "price": 150.00}
]
```

## 🔧 Comandos Útiles

```bash
# Desarrollo
python manage.py runserver              # Levantar servidor
python manage.py shell                  # Django shell
python manage.py makemigrations         # Crear migraciones
python manage.py migrate                # Aplicar migraciones

# Base de datos
python manage.py createsuperuser        # Crear admin
python manage.py flush                  # Limpiar BD
python manage.py loaddata fixture.json  # Cargar datos

# Testing
python manage.py test                   # Ejecutar tests
python manage.py test apps.business     # Tests específicos

# Producción
python manage.py collectstatic         # Archivos estáticos
python manage.py check --deploy        # Verificar configuración
```

## 🎨 Personalización

### Validaciones Personalizadas
```python
class ProductSerializer(BaseModelSerializer):
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value

    def validate_code(self, value):
        if not value.startswith('PROD'):
            raise serializers.ValidationError("El código debe empezar con 'PROD'")
        return value
```

### Campos Calculados
```python
class ProductSerializer(BaseModelSerializer):
    price_with_tax = serializers.SerializerMethodField()

    def get_price_with_tax(self, obj):
        return float(obj.price) * 1.12  # IVA 12%
```

### Filtros Personalizados
```python
import django_filters

class ProductFilterSet(django_filters.FilterSet):
    price_range = django_filters.RangeFilter(field_name='price')
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['is_active', 'price_range', 'name']

class ProductViewSet(BaseModelViewSet):
    filterset_class = ProductFilterSet
```

## 🌐 URLs Principales

- **Admin:** `http://localhost:8000/admin/`
- **API Root:** `http://localhost:8000/api/v1/`
- **Swagger:** `http://localhost:8000/swagger/`
- **API Auth:** `http://localhost:8000/api-auth/login/`

## 🔒 Configuración de Seguridad

### Variables de Entorno (.env)
```bash
SECRET_KEY=tu-clave-secreta-muy-larga
DEBUG=True
DB_NAME=mi_database
DB_USER=usuario
DB_PASSWORD=password123
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Permisos por Defecto
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## 📚 Casos de Uso Comunes

### Sistema de Inventario
- `Product`, `Category`, `Supplier`
- Filtros por categoría, stock, precio
- Reportes de inventario

### Sistema de RRHH
- `Employee`, `Department`, `Position`
- Filtros por departamento, estado
- Gestión de personal

### Sistema de Ventas
- `Customer`, `Order`, `OrderItem`
- Filtros por fecha, cliente, estado
- Reportes de ventas

## ⚡ Tips para Pruebas Técnicas

1. **Muestra la arquitectura** - Explica los mixins reutilizables
2. **Demuestra velocidad** - Crea un CRUD nuevo en 2 minutos
3. **Destaca validaciones** - Muestra validaciones robustas
4. **Usa el admin** - Interface profesional lista
5. **Menciona escalabilidad** - Fácil añadir nuevos módulos

## 🧪 Testing

### Estructura de Tests
```python
# tests/test_products.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apps.business.models import Product

class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        data = {'code': 'TEST001', 'name': 'Test Product', 'price': 100.00}
        response = self.client.post('/api/v1/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(code='TEST001').exists())
```

## 🚢 Despliegue

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

## 📝 Logging

```python
# settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🚀 ¡Empieza a construir APIs en minutos!

Esta plantilla te permite enfocarte en la **lógica de negocio** mientras las funcionalidades comunes ya están resueltas. Perfecto para prototipos rápidos, MVPs y pruebas técnicas.

### 💡 Filosofía de la Plantilla

**"No repitas código, reutiliza patrones"**

- Un ViewSet → CRUD completo
- Un Modelo → Admin automático
- Un Serializer → Validaciones incluidas
- Una configuración → Múltiples entornos

**¡Construye más rápido, con menos código y mejor calidad!** 🎯