"""
Vistas DRF — Google Earth Engine (adquisición).

  GET  /api/gee/status/
  GET  /api/gee/capas/
  GET  /api/gee/capas/{layer_id}/tiles/
  GET|POST /api/gee/consulta-celda/
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.adquisicion.api.serializers import GeeConsultaCeldaSerializer
from apps.adquisicion.services import GeeService, get_gee_service
from apps.escenarios.models import Escenario
from apps.usuarios.permissions import CanAuditRead, HasSadeRole


class GeeStatusAPIView(APIView):
    """Estado GEE (ready / degraded). Público para smoke tests."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(get_gee_service().status())


class GeeCapasAPIView(APIView):
    """GET capas GEE disponibles + TileURL XYZ."""

    permission_classes = [IsAuthenticated, HasSadeRole, CanAuditRead]

    def get(self, request):
        include_tiles = str(
            request.query_params.get("tiles", "1")
        ).lower() not in ("0", "false", "no")
        svc = get_gee_service()
        capas = svc.list_layers(include_tiles=include_tiles)
        return Response(
            {
                "crs_gee": "EPSG:4326",
                "crs_analisis": "EPSG:32613",
                "roi_bbox_4326": svc.status()["roi_valles_bbox_4326"],
                "gee": {
                    "mode": svc.status()["mode"],
                    "available": svc.status()["available"],
                    "message": svc.status()["message"],
                },
                "capas": capas,
            }
        )


class GeeCapaTilesAPIView(APIView):
    """GET /api/gee/capas/<layer_id>/tiles/ — mapid + plantilla XYZ."""

    permission_classes = [IsAuthenticated, HasSadeRole, CanAuditRead]

    def get(self, request, layer_id: str):
        svc = get_gee_service()
        meta = GeeService.get_layer_meta(layer_id)
        if meta is None:
            return Response(
                {"detail": f"Capa desconocida: {layer_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            mid = svc.get_map_id(layer_id)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "layer_id": layer_id,
                "nombre": meta["nombre"],
                "mapid": mid.mapid,
                "token": mid.token,
                "tile_url_template": mid.tile_url_template,
                "vis_params": mid.vis_params,
                "degraded": mid.degraded,
                "detail": mid.detail,
                "crs": "EPSG:4326",
            }
        )


class GeeConsultaCeldaAPIView(APIView):
    """
    GET/POST consulta celda con reduceRegion (o híbrido con escenario).

    Query/body: lat,lon | x,y · opcional escenario_id, scale_m, layer_ids.
    """

    permission_classes = [IsAuthenticated, HasSadeRole, CanAuditRead]

    def get(self, request):
        return self._handle(request.query_params)

    def post(self, request):
        data = request.data if hasattr(request, "data") else {}
        # Permitir mezcla query + body
        merged = {**request.query_params.dict(), **dict(data)}
        return self._handle(merged)

    def _handle(self, raw):
        ser = GeeConsultaCeldaSerializer(data=raw)
        ser.is_valid(raise_exception=True)
        q = ser.validated_data
        escenario = None
        if q.get("escenario_id"):
            try:
                escenario = Escenario.objects.get(pk=q["escenario_id"])
            except Escenario.DoesNotExist:
                return Response(
                    {"detail": "Escenario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        svc = get_gee_service()
        try:
            ficha = svc.ficha_consulta_celda(
                lon=q.get("lon"),
                lat=q.get("lat"),
                x=q.get("x"),
                y=q.get("y"),
                escenario=escenario,
                scale_m=float(q.get("scale_m") or 30.0),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ficha)
