"""API views for scenario execution, sensitivity, and map exports (PASO 4)."""
from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.escenarios.models import Escenario
from apps.escenarios.serializers import (
    EjecutarEscenarioSerializer,
    EscenarioSerializer,
    SensibilidadSerializer,
)
from apps.escenarios.services import EscenarioExecutionService
from apps.multicriterio.models import ConjuntoPesosAHP
from apps.usuarios.permissions import CanAuditRead, CanExecuteEscenario, HasSadeRole


class EscenarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List/retrieve escenarios + execute / re-execute / map actions.

    Permissions: authenticated + SADE role hooks (staff bypasses in tests).
    """

    queryset = Escenario.objects.select_related("conjunto_pesos").all()
    serializer_class = EscenarioSerializer
    permission_classes = [IsAuthenticated, HasSadeRole]

    def get_permissions(self):
        if self.action in ("ejecutar", "reejecutar"):
            return [IsAuthenticated(), CanExecuteEscenario()]
        if self.action in ("geojson", "tilejson", "tiles_stub", "sensibilidad"):
            return [IsAuthenticated(), CanAuditRead()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="ejecutar")
    def ejecutar(self, request):
        ser = EjecutarEscenarioSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        conjunto = ConjuntoPesosAHP.objects.get(pk=data["conjunto_pesos_id"])
        service = EscenarioExecutionService()
        out = service.execute(
            nombre=data["nombre"],
            version_reglas_usada=data["version_reglas_usada"],
            conjunto_pesos=conjunto,
            parametros_ejecucion=data.get("parametros_ejecucion") or {},
            weights_from_db=data.get("weights_from_db", True),
        )
        payload = EscenarioSerializer(out.escenario).data
        payload["created"] = out.created
        return Response(
            payload,
            status=status.HTTP_201_CREATED if out.created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="reejecutar")
    def reejecutar(self, request, pk=None):
        escenario = self.get_object()
        service = EscenarioExecutionService()
        out = service.reexecute(escenario)
        return Response(
            {
                "escenario": EscenarioSerializer(out.escenario).data,
                "hash_configuracion": out.hash_configuracion,
                "hash_resultado_anterior": out.hash_resultado_anterior,
                "hash_resultado_nuevo": out.hash_resultado_nuevo,
                "config_unchanged": out.config_unchanged,
                "resultado_reproducido": out.resultado_reproducido,
            }
        )

    @action(detail=False, methods=["post"], url_path="sensibilidad")
    def sensibilidad(self, request):
        ser = SensibilidadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        conjunto = ConjuntoPesosAHP.objects.get(pk=data["conjunto_pesos_id"])
        service = EscenarioExecutionService()
        report = service.sensitivity_e0_e8(
            version_reglas_usada=data["version_reglas_usada"],
            conjunto_pesos=conjunto,
            parametros_ejecucion=data.get("parametros_ejecucion") or {},
            persist=data.get("persist", False),
        )
        return Response(
            {
                "baseline_id": report.baseline_id,
                "notes": report.notes,
                "experiments": report.experiments,
                "pairwise_jaccard": [
                    {
                        "scenario_a": p.scenario_a,
                        "scenario_b": p.scenario_b,
                        "jaccard": p.jaccard,
                        "intersection_cells": p.intersection_cells,
                        "union_cells": p.union_cells,
                    }
                    for p in report.pairwise_jaccard
                ],
            }
        )

    @action(detail=True, methods=["get"], url_path="geojson")
    def geojson(self, request, pk=None):
        escenario = self.get_object()
        geo = (escenario.resultados_json or {}).get("geojson")
        if not geo:
            # Rebuild features if missing (legacy rows)
            service = EscenarioExecutionService()
            class_map = (escenario.resultados_json or {}).get("class_map")
            suitability = (escenario.resultados_json or {}).get("suitability")
            if class_map is None:
                return Response(
                    {"detail": "Escenario sin resultados_json.class_map"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            import numpy as np

            features = service._class_map_to_geojson_features(
                np.asarray(class_map),
                np.asarray(suitability if suitability is not None else class_map),
            )
            geo = {"type": "FeatureCollection", "features": features}
        # Attach audit props at collection level
        geo = {
            **geo,
            "sade_audit": {
                "escenario_id": escenario.pk,
                "hash_configuracion": escenario.hash_configuracion,
                "hash_resultado": escenario.hash_resultado,
                "crs": "EPSG:32613",
            },
        }
        return Response(geo)

    @action(detail=True, methods=["get"], url_path="tilejson")
    def tilejson(self, request, pk=None):
        escenario = self.get_object()
        service = EscenarioExecutionService()
        base = request.build_absolute_uri("/").rstrip("/")
        return Response(service.tilejson_contract(escenario, request_base=base))

    @action(
        detail=True,
        methods=["get"],
        url_path=r"tiles/(?P<z>[0-9]+)/(?P<x>[0-9]+)/(?P<y>[0-9]+).png",
    )
    def tiles_stub(self, request, pk=None, z=None, x=None, y=None):
        """Placeholder XYZ tile — returns 501 until tiling stack is ready."""
        return Response(
            {
                "detail": "Tile rendering not implemented (stub).",
                "z": z,
                "x": x,
                "y": y,
                "hint": f"Use /api/escenarios/{pk}/geojson/ for v1 maps.",
            },
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class HealthAPIView(APIView):
    """Unauthenticated health check for smoke tests."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "sade-api", "paso": 4})
