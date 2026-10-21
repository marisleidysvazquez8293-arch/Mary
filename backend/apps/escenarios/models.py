"""
Escenarios de ejecución multicriterio.
"""
from django.db import models

from apps.multicriterio.models import ConjuntoPesosAHP


class Escenario(models.Model):
    nombre = models.CharField("Nombre", max_length=255)
    version_reglas_usada = models.CharField(
        "Versión de reglas usada",
        max_length=64,
        help_text="Identificador/versión del conjunto de reglas aplicado.",
    )
    conjunto_pesos = models.ForeignKey(
        ConjuntoPesosAHP,
        on_delete=models.PROTECT,
        related_name="escenarios",
        verbose_name="Conjunto de pesos AHP",
    )
    hash_configuracion = models.CharField(
        "Hash de configuración",
        max_length=128,
        unique=True,
        help_text="Hash único de la configuración del escenario.",
    )
    hash_resultado = models.CharField(
        "Hash de resultado",
        max_length=128,
        blank=True,
        default="",
        help_text="Hash del resultado espacial (vacío hasta ejecutar).",
    )
    fecha_ejecucion = models.DateTimeField(
        "Fecha de ejecución",
        null=True,
        blank=True,
        help_text="Momento de la última ejecución exitosa.",
    )
    parametros_ejecucion = models.JSONField(
        "Parámetros de ejecución",
        default=dict,
        blank=True,
        help_text="Parámetros de corrida (resolución, extent, etc.).",
    )
    resultados_json = models.JSONField(
        "Resultados (JSON)",
        default=dict,
        blank=True,
        help_text="Superficies / métricas por clase de idoneidad.",
    )

    class Meta:
        verbose_name = "Escenario"
        verbose_name_plural = "Escenarios"
        ordering = ["-fecha_ejecucion", "nombre"]
        indexes = [
            models.Index(
                fields=["hash_configuracion"],
                name="esc_hash_config_idx",
            ),
            models.Index(
                fields=["fecha_ejecucion"],
                name="esc_fecha_ejecucion_idx",
            ),
            models.Index(
                fields=["version_reglas_usada"],
                name="esc_version_reglas_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.hash_configuracion[:12]})"
