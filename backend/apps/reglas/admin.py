from django.contrib import admin

from .models import Criterio, Regla


@admin.register(Criterio)
class CriterioAdmin(admin.ModelAdmin):
    list_display = (
        "id_criterio",
        "nombre",
        "bloque",
        "fuente",
        "tipo_restriccion",
        "activo",
    )
    list_filter = ("bloque", "tipo_restriccion", "activo", "fuente")
    search_fields = ("id_criterio", "nombre", "fuente")
    ordering = ("id_criterio",)


@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display = (
        "criterio",
        "version",
        "es_regla_respaldo",
        "descripcion_corta",
    )
    list_filter = ("es_regla_respaldo", "criterio__bloque", "version")
    search_fields = (
        "criterio__id_criterio",
        "criterio__nombre",
        "version",
        "descripcion",
    )
    autocomplete_fields = ("criterio",)
    ordering = ("criterio__id_criterio", "version")

    @admin.display(description="Descripción")
    def descripcion_corta(self, obj: Regla) -> str:
        text = obj.descripcion or ""
        return text[:80] + ("…" if len(text) > 80 else "")
