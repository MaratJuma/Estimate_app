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
    estimate_delete,

    contractor_create,
    contractor_detail,
    contractor_update,
    contractor_list,

    service_create,
    service_detail,
    service_create_for_contractor,
    service_update,
    service_delete,

    estimate_print,
    estimate_approve,
    estimate_excel_export,

    estimate_item_create_for_service,

    admin_dashboard,
    admin_category_list,
    admin_category_create,
    admin_category_update,
    admin_category_delete,

    admin_user_list,
    admin_user_create,
    admin_user_update,
    admin_user_delete,
    admin_import_database,
    
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
    path(
        'estimate-days/<int:day_id>/items/add/<int:service_id>/', 
        estimate_item_create_for_service, 
        name='estimate_item_create_for_service'
    ),
    path('estimate-days/<int:day_id>/delete/', estimate_day_delete, name='estimate_day_delete'),

    path('estimate-items/<int:item_id>/edit/', estimate_item_update, name='estimate_item_update'),
    path('estimate-items/<int:item_id>/delete/', estimate_item_delete, name='estimate_item_delete'),

    path('contractors/create/', contractor_create, name='contractor_create'),
    path('contractors/', contractor_list, name='contractor_list'),
    path('contractors/<int:contractor_id>/', contractor_detail, name='contractor_detail'),
    path('contractors/<int:contractor_id>/edit/', contractor_update, name='contractor_update'),

    path('services/create/', service_create, name='service_create'),
    path('contractors/<int:contractor_id>/services/create/', service_create_for_contractor, name='service_create_for_contractor'),
    path('services/<int:service_id>/', service_detail, name='service_detail'),
    path('services/<int:service_id>/edit/', service_update, name='service_update'),
    path('services/<int:service_id>/delete/', service_delete, name='service_delete'),

    path('estimates/<int:estimate_id>/print/', estimate_print, name='estimate_print'),
    path('estimates/<int:estimate_id>/approve/', estimate_approve, name='estimate_approve'),
    path('estimates/<int:estimate_id>/delete/', estimate_delete, name='estimate_delete'),
    path('estimates/<int:estimate_id>/excel/', estimate_excel_export, name='estimate_excel_export'),

    path('management/', admin_dashboard, name='admin_dashboard'),
    path('management/categories/', admin_category_list, name='admin_category_list'),
    path('management/categories/create/', admin_category_create, name='admin_category_create'),
    path('management/categories/<int:category_id>/edit/', admin_category_update, name='admin_category_update'),
    path('management/categories/<int:category_id>/delete/', admin_category_delete, name='admin_category_delete'),   

    path('management/users/', admin_user_list, name='admin_user_list'),
    path('management/users/create/', admin_user_create, name='admin_user_create'),
    path('management/users/<int:user_id>/edit/', admin_user_update, name='admin_user_update'),
    path('management/users/<int:user_id>/delete/', admin_user_delete, name='admin_user_delete'), 
    path('management/import/', admin_import_database, name='admin_import_database'),
]