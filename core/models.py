from django.db import models

class Contractor(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        related_name='services'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
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

    def days_count(self):
        return self.days.count()

    def __str__(self):
        return f"Смета #{self.id} - {self.client_name}"


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