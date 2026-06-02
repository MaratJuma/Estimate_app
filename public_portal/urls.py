from django.urls import path
from .views import home, register_company, register_success

urlpatterns = [
    path("", home, name="public_home"),
    path("register/", register_company, name="public_register_company"),
    path("register/success/", register_success, name="public_register_success"),
]