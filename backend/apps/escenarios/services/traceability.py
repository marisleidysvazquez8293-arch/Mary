"""
ScenarioTraceabilityService — hash de configuración y paquete ZIP (RNF-002 / RF-039).
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Mapping

from django.conf import settings

from apps.adquisicion.models import CapaGeoespacial
from apps.escenarios.hashing import canonical_json, hash_configuracion, sha256_hex
from apps.escenarios.models import Escenario
from apps.multicriterio.models import PesoCriterio
from apps.reglas.data.initial_rules import AHP_PROCEDENCIA, DEFAULT_REGLA_VERSION

SADE_SOFTWARE_VERSION = getattr(settings, "SADE_SOFTWARE_VERSION", "1.0.0")


class ScenarioTraceabilityService:
    """Trazabilidad de escenarios: SHA-256 de config y paquete de reproducibilidad."""

    def generar_hash_configuracion(self, escenario: Escenario) -> str:
        """
        SHA-256 canónico de reglas, capas referenciadas, pesos AHP y parámetros.

        Incluye más contexto que el hash persistido en Escenario.hash_configuracion
        (capas + snapshot de pesos), útil para auditoría / ZIP RNF-002.
        """
        pesos = list(
            PesoCriterio.objects.filter(conjunto_id=escenario.conjunto_pesos_id)
            .select_related("criterio")
            .order_by("criterio__id_criterio")
        )
        pesos_payload = [
            {
                "id_criterio": p.criterio.id_criterio,
                "peso_local": float(p.peso_local),
                "peso_global": float(p.peso_global),
            }
            for p in pesos
        ]
        capas_payload = self._capas_hashes(escenario)
        payload = {
            "capas": capas_payload,
            "conjunto_pesos_id": int(escenario.conjunto_pesos_id),
            "parametros_ejecucion": dict(escenario.parametros_ejecucion or {}),
            "pesos_ahp": pesos_payload,
            "software_version": SADE_SOFTWARE_VERSION,
            "version_reglas_usada": str(escenario.version_reglas_usada),
        }
        return sha256_hex(canonical_json(payload))

    def hash_configuracion_persistido(self, escenario: Escenario) -> str:
        """Recalcula el hash corto usado en Escenario.hash_configuracion."""
        return hash_configuracion(
            version_reglas_usada=escenario.version_reglas_usada,
            conjunto_pesos_id=escenario.conjunto_pesos_id,
            parametros_ejecucion=escenario.parametros_ejecucion or {},
        )

    def _capas_hashes(self, escenario: Escenario) -> list[dict[str, Any]]:
        refs = (escenario.parametros_ejecucion or {}).get("capas_ids") or []
        qs = CapaGeoespacial.objects.all()
        if refs:
            qs = qs.filter(pk__in=refs)
        else:
            qs = qs.none()
        rows = [
            {
                "id": c.pk,
                "nombre": c.nombre,
                "version": c.version,
                "hash_contenido": c.hash_contenido,
                "srid": c.srid,
                "ruta_o_id": c.ruta_archivo_o_id_gee,
            }
            for c in qs.order_by("id")
        ]
        # Fallback: hashes declarados en parámetros (demos sin filas CapaGeoespacial)
        declared = (escenario.parametros_ejecucion or {}).get("capas_hashes") or []
        if declared and not rows:
            return list(declared)
        return rows

    def generar_paquete_reproducibilidad(self, escenario_id: int) -> bytes:
        """
        ZIP (RF-039 / RNF-002): JSON config, hashes de capas, pesos, versión software.
        """
        escenario = Escenario.objects.select_related("conjunto_pesos").get(
            pk=escenario_id
        )
        conjunto = escenario.conjunto_pesos
        pesos = list(
            PesoCriterio.objects.filter(conjunto=conjunto)
            .select_related("criterio")
            .order_by("criterio__id_criterio")
        )
        config = {
            "escenario_id": escenario.pk,
            "nombre": escenario.nombre,
            "version_reglas_usada": escenario.version_reglas_usada,
            "hash_configuracion": escenario.hash_configuracion,
            "hash_configuracion_trazabilidad": self.generar_hash_configuracion(
                escenario
            ),
            "hash_resultado": escenario.hash_resultado,
            "fecha_ejecucion": (
                escenario.fecha_ejecucion.isoformat()
                if escenario.fecha_ejecucion
                else None
            ),
            "parametros_ejecucion": escenario.parametros_ejecucion or {},
            "software_version": SADE_SOFTWARE_VERSION,
            "crs": "EPSG:32613",
            "instrucciones": (
                "Importar este paquete en otra instancia SADE, restaurar "
                "parametros_ejecucion y pesos, y reejecutar. El hash_resultado "
                "debe coincidir (RF-039)."
            ),
        }
        pesos_doc = {
            "conjunto": {
                "id": conjunto.pk,
                "nombre": conjunto.nombre,
                "descripcion": conjunto.descripcion,
                "cr_geohidro": conjunto.cr_geohidro,
                "cr_ecol": conjunto.cr_ecol,
                "cr_socio": conjunto.cr_socio,
                "es_agregado_grupo": conjunto.es_agregado_grupo,
            },
            "procedencia": AHP_PROCEDENCIA,
            "version_reglas_default": DEFAULT_REGLA_VERSION,
            "pesos": [
                {
                    "id_criterio": p.criterio.id_criterio,
                    "nombre": p.criterio.nombre,
                    "bloque": p.criterio.bloque,
                    "peso_local": p.peso_local,
                    "peso_global": p.peso_global,
                }
                for p in pesos
            ],
        }
        capas = {"capas": self._capas_hashes(escenario)}
        meta = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "software_version": SADE_SOFTWARE_VERSION,
            "formato": "sade-reproducibilidad-v1",
            "rnf": "RNF-002",
            "rf": "RF-039",
        }

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("config.json", _pretty(config))
            zf.writestr("pesos_ahp.json", _pretty(pesos_doc))
            zf.writestr("capas_hashes.json", _pretty(capas))
            zf.writestr("software.json", _pretty(meta))
            # Resumen de resultados sin mapas enormes (class_counts + hashes)
            resumen = {
                "hash_resultado": escenario.hash_resultado,
                "class_counts": (escenario.resultados_json or {}).get(
                    "class_counts", {}
                ),
                "weights_used": (escenario.resultados_json or {}).get(
                    "weights_used", []
                ),
            }
            zf.writestr("resultados_resumen.json", _pretty(resumen))
        return buf.getvalue()


def _pretty(payload: Mapping[str, Any] | dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
