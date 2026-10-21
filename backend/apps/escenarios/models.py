"""
Escenarios de ejecución multicriterio (PASO 1).

hash_configuracion identifica de forma única la configuración usada;
resultados_json guarda superficies por clase de idoneidad.
"""
from django.db import models

from apps.multicriterio.models import ConjuntoPesosAHP


class Escenario(models.Model):
    nombre = models.CharField(max_length=255)
    version_reglas_usada = models.CharField(
        max_length=64,
        help_text="Identificador/versión del conjunto de reglas aplicado.",
    )
    conjunto_pesos = models.ForeignKey(
        ConjuntoPesosAHP,
        on_delete=models.PROTECT,
        related_name="escenarios",
    )
    hash_configuracion = models.CharField(
        max_length=128,
        unique=True,
        help_text="Hash único de la configuración del escenario.",
    )
    hash_resultado = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Hash del resultado espacial (vacío hasta ejecutar).",
    )
    fecha_ejecucion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Momento de la última ejecución exitosa.",
    )
    parametros_ejecucion = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parámetros de corrida (resolución, extent, etc.).",
    )
    resultados_json = models.JSONField(
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
