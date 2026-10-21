"""
Catálogo de capas geoespaciales.

GeometryField (django.contrib.gis) puede añadirse después para footprints;
SRID de análisis por defecto: EPSG:32613.
"""
from django.db import models

from apps.reglas.models import Criterio


class CapaGeoespacial(models.Model):
    class TipoFormato(models.TextChoices):
        VECTORIAL = "vectorial", "Vectorial"
        RASTER = "raster", "Ráster"
        GEE = "gee", "Google Earth Engine"

    nombre = models.CharField("Nombre", max_length=255)
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="capas",
        verbose_name="Criterio",
        help_text="Criterio asociado (opcional).",
    )
    tipo_formato = models.CharField(
        "Tipo de formato", max_length=16, choices=TipoFormato.choices
    )
    ruta_archivo_o_id_gee = models.CharField(
        "Ruta de archivo o ID GEE",
        max_length=1024,
        help_text="Ruta local/objeto o asset ID de GEE.",
    )
    srid = models.IntegerField(
        "SRID",
        default=32613,
        help_text="SRID de la capa (análisis SADE: 32613).",
    )
    version = models.CharField("Versión", max_length=64, blank=True, default="")
    es_confidencial = models.BooleanField("Es confidencial", default=False)
    hash_contenido = models.CharField(
        "Hash de contenido",
        max_length=128,
        blank=True,
        default="",
        help_text="Hash del contenido para integridad / deduplicación.",
    )

    class Meta:
        verbose_name = "Capa geoespacial"
        verbose_name_plural = "Capas geoespaciales"
        ordering = ["nombre", "version"]
        indexes = [
            models.Index(fields=["nombre"], name="adq_capa_nombre_idx"),
            models.Index(fields=["hash_contenido"], name="adq_capa_hash_idx"),
            models.Index(
                fields=["tipo_formato", "srid"],
                name="adq_capa_fmt_srid_idx",
            ),
            models.Index(
                fields=["es_confidencial"],
                name="adq_capa_confidencial_idx",
            ),
        ]

    def __str__(self) -> str:
        ver = f" v{self.version}" if self.version else ""
        return f"{self.nombre}{ver} [{self.tipo_formato}]"
