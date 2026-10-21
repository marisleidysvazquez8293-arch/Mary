"""Escenario API routes under /api/."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.escenarios.views import EscenarioViewSet, HealthAPIView

router = DefaultRouter()
router.register(r"escenarios", EscenarioViewSet, basename="escenario")

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="api-health"),
    path("", include(router.urls)),
]
