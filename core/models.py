from django.db import models
from django.conf import settings

class Contractor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name
    

class ServiceCategory(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)
    sort_order = models.PositiveIntegerField('Порядок сортировки', default=0)

    class Meta:
        verbose_name = "Категория услуги"
        verbose_name_plural = "Категории услуг"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=255)

    category = models.ForeignKey(
        'ServiceCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name='Категория (справочник)',
    )
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    client_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Estimate(models.Model):
    client_name = models.CharField(max_length=255)
    manager_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    contract_number = models.CharField("Номер договора", max_length=100, db_index=True)
    contract_estimate_number = models.PositiveIntegerField("Номер сметы по договору")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_estimates',
        verbose_name='Создал',
    )

    def days_count(self):
        return self.days.count()

    def __str__(self):
        return f"Смета #{self.id} ({self.contract_number}/{self.contract_estimate_number}) - {self.client_name}"
    
    class Meta:
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=["contract_number", "contract_estimate_number"],
                name="unique_estimate_per_contract_number",
            ),
        ]


class EstimateDay(models.Model):
    estimate = models.ForeignKey(Estimate,on_delete=models.CASCADE,related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['day_number']
        constraints = [
            models.UniqueConstraint(fields=['estimate', 'day_number'], name='unique_day_number_per_estimate')
        ]

    def __str__(self):
        if self.title:
            return f'День {self.day_number}: {self.title}'
        return f'День {self.day_number}'


class EstimateItem(models.Model):
    estimate_day = models.ForeignKey(EstimateDay,on_delete=models.CASCADE,related_name='items')
    service = models.ForeignKey(Service,on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    client_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    total_client = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.service.name} ({self.qty})"
    

class CompanyProfile(models.Model):
    name = models.CharField("Название компании", max_length=255)
    tagline = models.CharField("Слоган", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    email = models.EmailField("E-mail", blank=True)
    site = models.CharField("Сайт", max_length=255, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)

    logo = models.ImageField(
        "Логотип",
        upload_to="company_logos/",
        blank=True,
        null=True,
    )

    manager_title = models.CharField(
        "Должность подписанта",
        max_length=255,
        default="Менеджер проекта",
        blank=True,
    )
    manager_name = models.CharField(
        "Имя подписанта по умолчанию",
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Профиль компании"
        verbose_name_plural = "Профиль компании"

    def __str__(self):
        return self.name