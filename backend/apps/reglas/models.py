"""
Reglas de restricción y criterios SADE (PASO 1).

Bloques: geohidrológico, ecológico, socioeconómico.
Códigos tipicos: GEO_01, ECO_01, SOC_01 (id_criterio).
"""
from django.db import models


class Criterio(models.Model):
    class Bloque(models.TextChoices):
        GEOHIDROLOGICO = "geohidrologico", "Geohidrológico"
        ECOLOGICO = "ecologico", "Ecológico"
        SOCIOECONOMICO = "socioeconomico", "Socioeconómico"

    class TipoRestriccion(models.TextChoices):
        NORMATIVA = "normativa", "Normativa"
        MODELO = "modelo", "Modelo"
        ADVERTENCIA = "advertencia", "Advertencia"

    id_criterio = models.CharField(
        max_length=32,
        unique=True,
        help_text="Código único del criterio (ej. GEO_01, ECO_01, SOC_01).",
    )
    nombre = models.CharField(max_length=255)
    bloque = models.CharField(max_length=32, choices=Bloque.choices)
    fuente = models.CharField(
        max_length=128,
        help_text="Fuente normativa o técnica (NOM-083, SEDESOL, etc.).",
    )
    tipo_restriccion = models.CharField(
        max_length=32,
        choices=TipoRestriccion.choices,
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Criterio"
        verbose_name_plural = "Criterios"
        ordering = ["id_criterio"]
        indexes = [
            models.Index(fields=["id_criterio"], name="reglas_criterio_id_idx"),
            models.Index(fields=["bloque", "activo"], name="reglas_criterio_bloque_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.id_criterio} — {self.nombre}"


class Regla(models.Model):
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.CASCADE,
        related_name="reglas",
    )
    version = models.CharField(
        max_length=32,
        help_text="Versión semver de la regla (ej. 1.0.0).",
    )
    parametros_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Buffers, umbrales y funciones de idoneidad.",
    )
    es_regla_respaldo = models.BooleanField(
        default=False,
        help_text="True si es regla de respaldo ante datos incompletos.",
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Regla"
        verbose_name_plural = "Reglas"
        ordering = ["criterio__id_criterio", "version"]
        indexes = [
            models.Index(fields=["version"], name="reglas_regla_version_idx"),
            models.Index(
                fields=["criterio", "version"],
                name="reglas_regla_crit_ver_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["criterio", "version"],
                name="reglas_regla_criterio_version_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.criterio.id_criterio}@{self.version}"
