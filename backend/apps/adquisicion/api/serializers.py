"""Serializers API GEE."""
from __future__ import annotations

from rest_framework import serializers


class GeeConsultaCeldaSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    x = serializers.FloatField(required=False, help_text="EPSG:32613")
    y = serializers.FloatField(required=False, help_text="EPSG:32613")
    escenario_id = serializers.IntegerField(required=False, allow_null=True)
    scale_m = serializers.FloatField(required=False, default=30.0)
    layer_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )

    def validate(self, attrs):
        has_ll = attrs.get("lat") is not None and attrs.get("lon") is not None
        has_xy = attrs.get("x") is not None and attrs.get("y") is not None
        if not (has_ll or has_xy):
            raise serializers.ValidationError(
                "Indique lat+lon (EPSG:4326) o x+y (EPSG:32613)."
            )
        return attrs


class GeeLayerTileSerializer(serializers.Serializer):
    layer_id = serializers.CharField()
