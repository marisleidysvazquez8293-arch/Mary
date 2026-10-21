"""Rutas /api/gee/."""
from django.urls import path

from apps.adquisicion.api.views import (
    GeeCapasAPIView,
    GeeCapaTilesAPIView,
    GeeConsultaCeldaAPIView,
    GeeStatusAPIView,
)

urlpatterns = [
    path("status/", GeeStatusAPIView.as_view(), name="gee-status"),
    path("capas/", GeeCapasAPIView.as_view(), name="gee-capas"),
    path(
        "capas/<str:layer_id>/tiles/",
        GeeCapaTilesAPIView.as_view(),
        name="gee-capa-tiles",
    ),
    path(
        "consulta-celda/",
        GeeConsultaCeldaAPIView.as_view(),
        name="gee-consulta-celda",
    ),
]
