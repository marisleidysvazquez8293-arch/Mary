"""
Conjuntos de pesos AHP y pesos por criterio (Apéndice B).
"""
from django.db import models

from apps.reglas.models import Criterio


class ConjuntoPesosAHP(models.Model):
    nombre = models.CharField("Nombre", max_length=255)
    descripcion = models.TextField("Descripción", blank=True)
    cr_geohidro = models.FloatField(
        "CR geohidrológico",
        help_text="Razón de consistencia del bloque geohidrológico.",
    )
    cr_ecol = models.FloatField(
        "CR ecológico",
        help_text="Razón de consistencia del bloque ecológico.",
    )
    cr_socio = models.FloatField(
        "CR socioeconómico",
        help_text="Razón de consistencia del bloque socioeconómico.",
    )
    es_agregado_grupo = models.BooleanField(
        "Es agregado de grupo",
        default=False,
        help_text="Verdadero si agrega juicios de un grupo de expertos (AIJ).",
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)

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
        verbose_name="Conjunto AHP",
    )
    criterio = models.ForeignKey(
        Criterio,
        on_delete=models.PROTECT,
        related_name="pesos_ahp",
        verbose_name="Criterio",
    )
    peso_local = models.FloatField(
        "Peso local",
        help_text="Peso local dentro del bloque AHP.",
    )
    peso_global = models.FloatField(
        "Peso global",
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
