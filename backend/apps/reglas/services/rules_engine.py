"""
RulesEngineService — motor de reglas espaciales (EPSG:32613).

Máscara de exclusión ∏ c_j, buffers NOM-083 (500 m agua/pozos), ANP,
advertencia aeródromo <13 km (sin excluir ni bajar aptitud) y reglas de
respaldo (p. ej. 500 m si falta cono de abatimiento).

Alias de compatibilidad: ``ReglasEngineService = RulesEngineService``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

# IDs Tabla 4.1 (tesis)
WATER_IDS = frozenset({"ECO_01"})
WELLS_IDS = frozenset({"ECO_02"})
ANP_IDS = frozenset({"ECO_04"})
AERODROME_IDS = frozenset({"SOC_01"})
URBAN_IDS = frozenset({"SOC_02"})
DEFAULT_BUFFER_M = 500.0
DEFAULT_AERODROME_WARNING_M = 13_000.0
AERODROME_LABEL = "requiere estudio de riesgo aviario"


@dataclass(frozen=True)
class RestrictionLayer:
    """Capa de restricción que aporta al producto ∏ c_j."""

    id_criterio: str
    tipo_restriccion: str  # normativa | modelo | advertencia
    mask: np.ndarray  # True/1 = permitido
    parametros: Mapping[str, Any] = field(default_factory=dict)
    hard_exclude: bool = True


@dataclass
class WarningZone:
    id_criterio: str
    radius_m: float
    message: str
    cell_mask: np.ndarray | None = None
    etiqueta: str = ""


@dataclass
class ExclusionResult:
    """Resultado de conjunción de restricciones."""

    exclusion_mask: np.ndarray  # True = permitido
    product: np.ndarray  # ∏ c_j ∈ {0,1}
    warnings: list[WarningZone] = field(default_factory=list)
    applied_criteria: list[str] = field(default_factory=list)
    buffers_applied_m: dict[str, float] = field(default_factory=dict)
    reglas_respaldo_aplicadas: list[str] = field(default_factory=list)


@dataclass
class EscenarioConfigEspacial:
    """
    Configuración espacial mínima para generar exclusión.

    Capas: máscaras booleanas o rásteres de distancia (metros).
    """

    shape: tuple[int, int]
    capas: Mapping[str, Any] = field(default_factory=dict)
    # capas[id] = {"mask": ndarray} | {"distance_m": ndarray, "parametros": {...}}
    # | {"ausente": True} para disparar regla de respaldo
    srid: int = 32613


class RulesEngineService:
    """
    Motor de reglas NOM-083 / Tabla 4.1 (análisis en EPSG:32613).
    """

    def __init__(self, default_srid: int = 32613):
        self.default_srid = default_srid

    # ------------------------------------------------------------------
    # Helpers de parámetros
    # ------------------------------------------------------------------

    @staticmethod
    def buffer_meters(
        parametros: Mapping[str, Any] | None,
        default: float = DEFAULT_BUFFER_M,
    ) -> float:
        if not parametros:
            return default
        if "buffer_m" in parametros:
            return float(parametros["buffer_m"])
        return default

    @staticmethod
    def aerodrome_warning_radius_m(parametros: Mapping[str, Any] | None) -> float:
        if not parametros:
            return DEFAULT_AERODROME_WARNING_M
        if "warning_radius_m" in parametros:
            return float(parametros["warning_radius_m"])
        return DEFAULT_AERODROME_WARNING_M

    @staticmethod
    def is_hard_exclusion(
        tipo_restriccion: str,
        parametros: Mapping[str, Any] | None,
    ) -> bool:
        params = parametros or {}
        if "hard_exclude" in params:
            return bool(params["hard_exclude"])
        return tipo_restriccion != "advertencia"

    def aplicar_regla_respaldo_pozos(
        self,
        *,
        distance_m: np.ndarray | None,
        cono_abatimiento_disponible: bool,
        parametros: Mapping[str, Any] | None = None,
    ) -> tuple[np.ndarray, str | None]:
        """
        NOM-083 §6.1.7: si no hay cono de abatimiento → buffer respaldo 500 m.
        """
        params = dict(parametros or {})
        if distance_m is None:
            raise ValueError("Se requiere distance_m para pozos")
        if cono_abatimiento_disponible and "buffer_cono_m" in params:
            buf = float(params["buffer_cono_m"])
            nota = None
        else:
            buf = self.buffer_meters(params, default=DEFAULT_BUFFER_M)
            nota = (
                f"Regla de respaldo ECO_02: sin cono de abatimiento → "
                f"buffer {buf:.0f} m (NOM-083 §6.1.7)."
            )
            params["buffer_m"] = buf
            params["es_regla_respaldo"] = True
        mask = self.apply_distance_buffer_mask(distance_m, buf)
        return mask, nota

    # ------------------------------------------------------------------
    # API tesis
    # ------------------------------------------------------------------

    def generar_capa_exclusion(
        self,
        escenario_config: EscenarioConfigEspacial | Mapping[str, Any],
    ) -> ExclusionResult:
        """
        Genera máscara de exclusión (1=permitido, 0=excluido) = ∏ c_j.

        Aplica buffers 500 m a agua/pozos y exclusión de ANP cuando las
        capas están en ``escenario_config``.
        """
        if isinstance(escenario_config, Mapping):
            shape = tuple(escenario_config["shape"])
            capas = dict(escenario_config.get("capas") or {})
            srid = int(escenario_config.get("srid", self.default_srid))
            cfg = EscenarioConfigEspacial(shape=shape, capas=capas, srid=srid)
        else:
            cfg = escenario_config

        if cfg.srid != 32613:
            # Análisis SADE se declara en UTM 13N; se acepta override documentado
            pass

        layers: list[RestrictionLayer] = []
        respaldos: list[str] = []

        # Agua superficial — buffer 500 m
        water = cfg.capas.get("ECO_01") or cfg.capas.get("agua_superficial")
        if water is not None:
            layer, nota = self._layer_from_capa(
                "ECO_01", "normativa", water, default_buffer=DEFAULT_BUFFER_M
            )
            layers.append(layer)
            if nota:
                respaldos.append(nota)

        # Pozos — respaldo 500 m si falta cono
        wells = cfg.capas.get("ECO_02") or cfg.capas.get("pozos")
        if wells is not None:
            layer, nota = self._layer_pozos(wells)
            layers.append(layer)
            if nota:
                respaldos.append(nota)

        # ANP — exclusión dura
        anp = cfg.capas.get("ECO_04") or cfg.capas.get("anp")
        if anp is not None:
            layer, nota = self._layer_from_capa(
                "ECO_04", "normativa", anp, default_buffer=0.0
            )
            layers.append(layer)
            if nota:
                respaldos.append(nota)

        # Otras capas de exclusión explícitas en config
        for key, capa in cfg.capas.items():
            if key in ("ECO_01", "ECO_02", "ECO_04", "agua_superficial", "pozos", "anp"):
                continue
            if key in AERODROME_IDS or key in ("aerodromo", "SOC_01"):
                continue  # advertencia, no exclusión
            if not isinstance(capa, Mapping):
                continue
            if capa.get("excluir", True) is False:
                continue
            tipo = str(capa.get("tipo_restriccion", "normativa"))
            if tipo == "advertencia":
                continue
            layer, nota = self._layer_from_capa(
                str(key), tipo, capa, default_buffer=float(capa.get("buffer_m", 0) or 0)
            )
            layers.append(layer)
            if nota:
                respaldos.append(nota)

        result = self.build_exclusion_mask(layers, shape=cfg.shape)
        result.reglas_respaldo_aplicadas = respaldos
        return result

    def aplicar_reglas_advertencia(
        self,
        *,
        distance_aerodromo_m: np.ndarray | None = None,
        parametros: Mapping[str, Any] | None = None,
        shape: tuple[int, int] | None = None,
    ) -> list[WarningZone]:
        """
        Advertencias sin exclusión ni reducción de aptitud.

        NOM-083 §6.1.1: <13 km al centro de pista → etiqueta
        «requiere estudio de riesgo aviario».
        """
        warnings: list[WarningZone] = []
        if distance_aerodromo_m is None:
            return warnings
        dist = np.asarray(distance_aerodromo_m, dtype=float)
        if shape is not None and dist.shape != shape:
            raise ValueError(f"shape aeródromo {dist.shape} != {shape}")
        radius = self.aerodrome_warning_radius_m(parametros)
        # Dentro del radio: advertencia (cell_mask True)
        warn_mask = dist < radius
        warnings.append(
            WarningZone(
                id_criterio="SOC_01",
                radius_m=radius,
                message=(
                    f"Aeródromo/aeropuerto a <{radius/1000:.0f} km: "
                    f"{AERODROME_LABEL} (NOM-083 §6.1.1)."
                ),
                cell_mask=warn_mask,
                etiqueta=AERODROME_LABEL,
            )
        )
        return warnings

    # ------------------------------------------------------------------
    # Núcleo ∏ c_j (API previa)
    # ------------------------------------------------------------------

    def build_exclusion_mask(
        self,
        layers: Sequence[RestrictionLayer],
        *,
        shape: tuple[int, int] | None = None,
    ) -> ExclusionResult:
        if not layers:
            if shape is None:
                raise ValueError("shape requerido si layers está vacío")
            ones = np.ones(shape, dtype=bool)
            return ExclusionResult(
                exclusion_mask=ones,
                product=ones.astype(float),
            )

        ref = np.asarray(layers[0].mask)
        if shape is None:
            shape = ref.shape
        product = np.ones(shape, dtype=float)
        warnings: list[WarningZone] = []
        applied: list[str] = []
        buffers: dict[str, float] = {}

        for layer in layers:
            mask = np.asarray(layer.mask, dtype=float)
            if mask.shape != shape:
                raise ValueError(
                    f"Shape mismatch for {layer.id_criterio}: {mask.shape} != {shape}"
                )
            c_j = (mask > 0).astype(float)
            hard = layer.hard_exclude and self.is_hard_exclusion(
                layer.tipo_restriccion, layer.parametros
            )
            applied.append(layer.id_criterio)

            buf = self.buffer_meters(layer.parametros, default=0.0)
            if buf > 0 and layer.id_criterio in (WATER_IDS | WELLS_IDS | URBAN_IDS | ANP_IDS):
                buffers[layer.id_criterio] = buf
            elif "buffer_m" in (layer.parametros or {}):
                buffers[layer.id_criterio] = float(layer.parametros["buffer_m"])

            if hard:
                product *= c_j
            else:
                warn_mask = c_j < 0.5
                radius = self.aerodrome_warning_radius_m(layer.parametros)
                if layer.id_criterio in AERODROME_IDS:
                    msg = (
                        f"Aeródromo/aeropuerto a <{radius/1000:.0f} km: "
                        f"{AERODROME_LABEL} (NOM-083 §6.1.1)."
                    )
                    etiqueta = AERODROME_LABEL
                else:
                    msg = f"Advertencia activa para {layer.id_criterio}."
                    etiqueta = ""
                warnings.append(
                    WarningZone(
                        id_criterio=layer.id_criterio,
                        radius_m=radius if layer.id_criterio in AERODROME_IDS else buf,
                        message=msg,
                        cell_mask=warn_mask,
                        etiqueta=etiqueta,
                    )
                )

        return ExclusionResult(
            exclusion_mask=product > 0.5,
            product=product,
            warnings=warnings,
            applied_criteria=applied,
            buffers_applied_m=buffers,
        )

    def apply_distance_buffer_mask(
        self,
        distance_raster_m: np.ndarray,
        buffer_m: float,
    ) -> np.ndarray:
        """Celdas con distancia >= buffer_m → permitido (True)."""
        dist = np.asarray(distance_raster_m, dtype=float)
        return dist >= float(buffer_m)

    def build_layers_from_distance_rasters(
        self,
        specs: Iterable[Mapping[str, Any]],
    ) -> list[RestrictionLayer]:
        layers: list[RestrictionLayer] = []
        for spec in specs:
            params = dict(spec.get("parametros") or {})
            buffer_m = self.buffer_meters(params, default=DEFAULT_BUFFER_M)
            if spec["id_criterio"] in AERODROME_IDS:
                radius = self.aerodrome_warning_radius_m(params)
                mask = np.asarray(spec["distance_m"], dtype=float) >= radius
                params.setdefault("warning_radius_m", radius)
            else:
                # Regla de respaldo pozos
                if spec["id_criterio"] in WELLS_IDS and params.get(
                    "cono_abatimiento_disponible"
                ) is False:
                    params.setdefault("buffer_m", DEFAULT_BUFFER_M)
                    params["es_regla_respaldo"] = True
                    buffer_m = DEFAULT_BUFFER_M
                mask = self.apply_distance_buffer_mask(spec["distance_m"], buffer_m)
                params.setdefault("buffer_m", buffer_m)

            tipo = spec.get("tipo_restriccion", "normativa")
            hard = spec.get("hard_exclude")
            if hard is None:
                hard = self.is_hard_exclusion(tipo, params)

            layers.append(
                RestrictionLayer(
                    id_criterio=spec["id_criterio"],
                    tipo_restriccion=tipo,
                    mask=mask,
                    parametros=params,
                    hard_exclude=hard,
                )
            )
        return layers

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _layer_from_capa(
        self,
        id_criterio: str,
        tipo: str,
        capa: Mapping[str, Any],
        *,
        default_buffer: float,
    ) -> tuple[RestrictionLayer, str | None]:
        nota = None
        params = dict(capa.get("parametros") or {})
        if capa.get("ausente"):
            # Sin geometría: todo permitido salvo que se indique lo contrario
            # (quien llama debe proveer shape vía otra capa)
            raise ValueError(
                f"Capa {id_criterio} marcada ausente sin máscara de respaldo explícita"
            )
        if "mask" in capa:
            mask = np.asarray(capa["mask"])
            # mask True/1 = permitido
        elif "distance_m" in capa:
            buf = self.buffer_meters(params, default=default_buffer)
            params.setdefault("buffer_m", buf)
            mask = self.apply_distance_buffer_mask(capa["distance_m"], buf)
        else:
            raise ValueError(f"Capa {id_criterio} requiere 'mask' o 'distance_m'")
        return (
            RestrictionLayer(
                id_criterio=id_criterio,
                tipo_restriccion=tipo,
                mask=mask,
                parametros=params,
                hard_exclude=True,
            ),
            nota,
        )

    def _layer_pozos(
        self,
        capa: Mapping[str, Any],
    ) -> tuple[RestrictionLayer, str | None]:
        params = dict(capa.get("parametros") or {})
        cono = bool(capa.get("cono_abatimiento_disponible", params.get("cono_abatimiento_disponible", False)))
        if "mask" in capa and cono:
            return (
                RestrictionLayer(
                    id_criterio="ECO_02",
                    tipo_restriccion="normativa",
                    mask=np.asarray(capa["mask"]),
                    parametros=params,
                    hard_exclude=True,
                ),
                None,
            )
        if "distance_m" not in capa:
            raise ValueError("ECO_02 requiere distance_m o mask")
        mask, nota = self.aplicar_regla_respaldo_pozos(
            distance_m=capa["distance_m"],
            cono_abatimiento_disponible=cono,
            parametros=params,
        )
        if nota:
            params["es_regla_respaldo"] = True
            params.setdefault("buffer_m", DEFAULT_BUFFER_M)
        return (
            RestrictionLayer(
                id_criterio="ECO_02",
                tipo_restriccion="normativa",
                mask=mask,
                parametros=params,
                hard_exclude=True,
            ),
            nota,
        )

    # ------------------------------------------------------------------
    # Stubs GIS / ORM
    # ------------------------------------------------------------------

    def buffer_geometries_stub(
        self,
        geometries: Any,
        distance_m: float,
        *,
        srid: int | None = None,
    ) -> Any:
        raise NotImplementedError(
            "buffer_geometries_stub: requiere shapely/geopandas "
            f"({distance_m} m, srid={srid or self.default_srid})."
        )

    def rasterize_mask_stub(
        self,
        geometries: Any,
        transform: Any,
        shape: tuple[int, int],
    ) -> np.ndarray:
        raise NotImplementedError(
            "rasterize_mask_stub: requiere rasterio."
        )

    def gee_exclusion_hook_stub(self, asset_ids: Sequence[str], region: Any) -> np.ndarray:
        raise NotImplementedError(
            f"gee_exclusion_hook_stub: no configurado (assets={list(asset_ids)})."
        )

    def active_rule_params_from_orm(self, version: str = "1.0.0") -> list[dict[str, Any]]:
        from apps.reglas.models import Criterio

        out: list[dict[str, Any]] = []
        qs = Criterio.objects.filter(activo=True).prefetch_related("reglas")
        for crit in qs:
            regla = crit.reglas.filter(version=version).first()
            if regla is None:
                regla = crit.reglas.order_by("-version").first()
            out.append(
                {
                    "id_criterio": crit.id_criterio,
                    "tipo_restriccion": crit.tipo_restriccion,
                    "bloque": crit.bloque,
                    "parametros": dict(regla.parametros_json) if regla else {},
                    "version": regla.version if regla else None,
                }
            )
        return out


# Compatibilidad con código previo
ReglasEngineService = RulesEngineService
