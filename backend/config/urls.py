"""SADE URL configuration — PASO 1 stub (no API views yet)."""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # PASO 2+: DRF routers for adquisicion, reglas, multicriterio, escenarios, etc.
]
