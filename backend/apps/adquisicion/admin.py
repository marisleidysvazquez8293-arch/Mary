from django.contrib import admin

from .models import CapaGeoespacial


@admin.register(CapaGeoespacial)
class CapaGeoespacialAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "criterio",
        "tipo_formato",
        "srid",
        "version",
        "es_confidencial",
        "hash_contenido",
    )
    list_filter = ("tipo_formato", "srid", "es_confidencial", "criterio__bloque")
    search_fields = (
        "nombre",
        "ruta_archivo_o_id_gee",
        "hash_contenido",
        "version",
        "criterio__id_criterio",
        "criterio__nombre",
    )
    autocomplete_fields = ("criterio",)
    ordering = ("nombre", "version")
