from django.contrib import admin
from .models import Contractor, Service, Estimate, EstimateDay, EstimateItem


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'contact_name', 'phone', 'email')
    search_fields = ('name', 'category', 'contact_name', 'phone', 'email')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contractor', 'cost_price', 'client_price', 'is_active')
    list_filter = ('is_active', 'contractor', 'contractor__category')
    search_fields = ('name', 'description')


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'manager_name', 'created_at')
    search_fields = ('client_name', 'manager_name')
    readonly_fields = ('created_at',)

@admin.register(EstimateDay)
class EstimateDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'day_number', 'estimate_id')


@admin.register(EstimateItem)
class EstimateItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'estimate_day', 'service', 'qty', 'total_cost', 'total_client')
    search_fields = ('service__name', 'estimate__client_name')