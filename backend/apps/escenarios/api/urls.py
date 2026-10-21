"""
Rutas REST bajo /api/.

Incluye:
  POST /api/escenarios/ejecutar/
  GET  /api/escenarios/{id}/mapa/
  GET  /api/escenarios/{id}/geojson/
  GET  /api/escenarios/{id}/tilejson/
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.escenarios.api.views import EscenarioViewSet, HealthAPIView

router = DefaultRouter()
router.register(r"escenarios", EscenarioViewSet, basename="escenario")

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="api-health"),
    path("", include(router.urls)),
]
