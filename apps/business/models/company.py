from django.db import  models
from apps.core.models import BaseModel

class Company(BaseModel):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200, verbose_name="Name")
    email = models.EmailField(blank=True, max_length=200, null=True, verbose_name="Email")
    phone = models.CharField(blank=True, max_length=20, null=True, verbose_name="Phone")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"