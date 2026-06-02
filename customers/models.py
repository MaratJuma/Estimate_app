from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    name = models.CharField("Название компании", max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    auto_create_schema = True

    class Meta:
        verbose_name = "Тенант"
        verbose_name_plural = "Тенанты"

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass