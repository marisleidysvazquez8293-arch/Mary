"""SADE URL configuration — API under /api/ (PASO 3–4)."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.escenarios.api.urls")),
]
