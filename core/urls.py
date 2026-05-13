from django.urls import path
from .views import (
    home,
    service_list,

    estimate_list,
    estimate_create,
    estimate_detail,
    estimate_update,
    estimate_duplicate,

    estimate_day_create,
    estimate_day_delete,
    estimate_day_update,

    estimate_item_create,
    estimate_item_delete,
    estimate_item_update,

    contractor_create,
    contractor_update,
    contractor_list,
    service_create,
    service_update,
    service_delete,

    estimate_print,
    estimate_approve,
    estimate_excel_export,
    )
urlpatterns = [
    path('', home, name='home'),
    path('services/', service_list, name='service_list'),
    path('estimates/', estimate_list, name='estimate_list'),
    path('estimates/create/', estimate_create, name='estimate_create'),
    path('estimates/<int:estimate_id>/edit/', estimate_update, name='estimate_update'),
    path('estimates/<int:estimate_id>/duplicate/', estimate_duplicate, name='estimate_duplicate'),
    path('estimates/<int:estimate_id>/days/add/', estimate_day_create, name='estimate_day_create'),
    path('days/<int:day_id>/edit/', estimate_day_update, name='estimate_day_update'),
    path('estimates/<int:estimate_id>/', estimate_detail, name='estimate_detail'),

    path('estimate-days/<int:day_id>/items/add/', estimate_item_create, name='estimate_item_create'),
    path('estimate-days/<int:day_id>/delete/', estimate_day_delete, name='estimate_day_delete'),

    path('estimate-items/<int:item_id>/edit/', estimate_item_update, name='estimate_item_update'),
    path('estimate-items/<int:item_id>/delete/', estimate_item_delete, name='estimate_item_delete'),

    path('contractors/create/', contractor_create, name='contractor_create'),
    path('contractors/', contractor_list, name='contractor_list'),
    path('contractors/<int:contractor_id>/edit/', contractor_update, name='contractor_update'),
    path('services/create/', service_create, name='service_create'),
    path('services/<int:service_id>/edit/', service_update, name='service_update'),
    path('services/<int:service_id>/delete/', service_delete, name='service_delete'),

    path('estimates/<int:estimate_id>/print/', estimate_print, name='estimate_print'),
    path('estimates/<int:estimate_id>/approve/', estimate_approve, name='estimate_approve'),
    path('estimates/<int:estimate_id>/excel/', estimate_excel_export, name='estimate_excel_export'),
    
]