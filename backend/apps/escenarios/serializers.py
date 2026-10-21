"""DRF serializers for Escenario API (PASO 4)."""
from __future__ import annotations

from rest_framework import serializers

from apps.escenarios.models import Escenario
from apps.multicriterio.models import ConjuntoPesosAHP


class EscenarioSerializer(serializers.ModelSerializer):
    conjunto_pesos_nombre = serializers.CharField(
        source="conjunto_pesos.nombre", read_only=True
    )

    class Meta:
        model = Escenario
        fields = [
            "id",
            "nombre",
            "version_reglas_usada",
            "conjunto_pesos",
            "conjunto_pesos_nombre",
            "hash_configuracion",
            "hash_resultado",
            "fecha_ejecucion",
            "parametros_ejecucion",
            "resultados_json",
        ]
        read_only_fields = [
            "hash_configuracion",
            "hash_resultado",
            "fecha_ejecucion",
            "resultados_json",
        ]


class EjecutarEscenarioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255)
    version_reglas_usada = serializers.CharField(max_length=64, default="1.0.0")
    conjunto_pesos_id = serializers.IntegerField()
    parametros_ejecucion = serializers.DictField(required=False, default=dict)
    weights_from_db = serializers.BooleanField(default=True)

    def validate_conjunto_pesos_id(self, value: int) -> int:
        if not ConjuntoPesosAHP.objects.filter(pk=value).exists():
            raise serializers.ValidationError("ConjuntoPesosAHP no existe.")
        return value


class ReejecutarSerializer(serializers.Serializer):
    """Empty body OK; path pk selects escenario."""

    pass


class SensibilidadSerializer(serializers.Serializer):
    version_reglas_usada = serializers.CharField(max_length=64, default="1.0.0")
    conjunto_pesos_id = serializers.IntegerField()
    parametros_ejecucion = serializers.DictField(required=False, default=dict)
    persist = serializers.BooleanField(
        default=False,
        help_text="Si true, persiste E0–E8 como Escenario rows.",
    )

    def validate_conjunto_pesos_id(self, value: int) -> int:
        if not ConjuntoPesosAHP.objects.filter(pk=value).exists():
            raise serializers.ValidationError("ConjuntoPesosAHP no existe.")
        return value


class SensitivityPairSerializer(serializers.Serializer):
    scenario_a = serializers.CharField()
    scenario_b = serializers.CharField()
    jaccard = serializers.FloatField()
    intersection_cells = serializers.IntegerField()
    union_cells = serializers.IntegerField()
