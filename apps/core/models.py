from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Modified")

    class Meta:
        abstract = True

class AuditModel(TimeStampedModel):
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_created',
        verbose_name="Created by",
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_updated',
        verbose_name="Updated by",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is active?",
    )

    class Meta:
        abstract = True

class BaseModel(AuditModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class CatalogModel(AuditModel):
    code = models.CharField(
        max_length=20,
        unique=True,

    )
    name = models.CharField(
        max_length=100,
        verbose_name="Name",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Order",
    )

    class Meta:
        abstract = True
        ordering = ('order', 'name')

    def __str__(self):
        return f"{self.code} - {self.name}"


class PersonModel(AuditModel):
    CEDULA_REGEX = RegexValidator(
        regex=r'^\d{10}$',
        message='La cédula debe tener exactamente 10 dígitos'
    )
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[CEDULA_REGEX],
        verbose_name="Cedula",
    )
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres",
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email",
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefono"
    )

    class Meta:
        abstract = True
        ordering = ('cedula', 'nombres')

    @property
    def nombre_completo(self):
        return f"{self.apellidos} ({self.nombres})"

    def __str__(self):
        return self._nombre_completo

class CompanyModel(AuditModel):
    RUC_REGEX = RegexValidator(
        regex=r'^\d{13}$',
        message="El RUC debe tener exactamente 13 dígitos"
    )
    ruc = models.CharField(
        max_length=13,
        unique=True,
        validators=[RUC_REGEX],
        verbose_name="RUC",
    )
    razon_social = models.CharField(
        max_length=200,
        verbose_name='Razán Social'
    )
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nombre Comercial",
    )
    direccion=models.TextField(
        blank=True,
        null=True,
        verbose_name="Direccion",
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefono",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email",
    )
    logo= models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True,
        verbose_name="Logo",
    )
    class Meta:
        abstract = True
        ordering = ['razon_social']

    def __str__(self):
        return self.nombre_comercial or self.razon_social


class SoftDeleteMixin(models.Model):
    deleted_at = (models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted at",
    ))
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_deleted',
        verbose_name="Deleted by",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def soft_deleted_at(self):
        self.deleted_at = timezone.now()
        self.deleted_by = User
        self.is_active = False
        self.save()


class SlugMixin(models.Model):
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name="Slug",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug and hasattr(self, 'name'):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
