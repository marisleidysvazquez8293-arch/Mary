"""
Conjuntos de pesos AHP y pesos por criterio (PASO 1).

cr_* almacenan el Consistency Ratio por bloque (geohidro / ecol / socio).
"""
from django.db import models

from apps.reglas.models import Criterio


class ConjuntoPesosAHP(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    cr_geohidro = models.FloatField(
        help_text="Consistency Ratio del bloque geohidrológico.",
    )
    cr_ecol = models.FloatField(
        help_text="Consistency Ratio del bloque ecológico.",
    )
    cr_socio = models.FloatField(
        help_text="Consistency Ratio del bloque socioeconómico.",
    )
    es_agregado_grupo = models.BooleanField(
        default=False,
        help_text="True si el conjunto agrega juicios de un grupo de expertos.",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conjunto de pesos AHP"
        verbose_name_plural = "Conjuntos de pesos AHP"
        ordering = ["-fecha_creacion"]
        indexes = [
            models.Index(fields=["nombre"], name="mc_ahp_nombre_idx"),
            models.Index(
                fields=["es_agregado_grupo", "fecha_creacion"],
                name="mc_ahp_grupo_fecha_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.nombre


class PesoCriterio(models.Model):
    conjunto = models.ForeignKey(
        ConjuntoPesosAHP,
        on_delete=models.CASCADE,
        related_name="pesos",
    )
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.PROTECT,
        related_name="pesos_ahp",
    )
    peso_local = models.FloatField(
        help_text="Peso local dentro del bloque AHP.",
    )
    peso_global = models.FloatField(
        help_text="Peso global respecto al objetivo de idoneidad.",
    )

    class Meta:
        verbose_name = "Peso de criterio"
        verbose_name_plural = "Pesos de criterio"
        ordering = ["conjunto", "criterio__id_criterio"]
        indexes = [
            models.Index(
                fields=["conjunto", "criterio"],
                name="mc_peso_conjunto_crit_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["conjunto", "criterio"],
                name="mc_peso_conjunto_criterio_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.conjunto.nombre} / {self.criterio.id_criterio}: {self.peso_global}"
