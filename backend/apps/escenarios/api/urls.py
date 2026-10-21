"""
Rutas REST bajo /api/ (PASO 4).

  GET  /api/health/
  POST /api/escenarios/ejecutar/
  POST /api/escenarios/sensibilidad/
  POST /api/escenarios/{id}/reejecutar/
  GET  /api/escenarios/{id}/mapa/
  GET  /api/escenarios/{id}/geojson/
  GET  /api/escenarios/{id}/tilejson/
  GET|POST /api/escenarios/{id}/hash/
  GET  /api/escenarios/{id}/reproducibilidad/   (ZIP)
  GET  /api/escenarios/{id}/pdf/
  GET  /api/escenarios/{id}/consulta-celda/
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
