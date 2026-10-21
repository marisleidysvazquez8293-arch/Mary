from django.contrib import admin

from .models import ConjuntoPesosAHP, PesoCriterio


class PesoCriterioInline(admin.TabularInline):
    model = PesoCriterio
    extra = 0
    autocomplete_fields = ("criterio",)


@admin.register(ConjuntoPesosAHP)
class ConjuntoPesosAHPAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "cr_geohidro",
        "cr_ecol",
        "cr_socio",
        "es_agregado_grupo",
        "fecha_creacion",
    )
    list_filter = ("es_agregado_grupo", "fecha_creacion")
    search_fields = ("nombre", "descripcion")
    ordering = ("-fecha_creacion",)
    inlines = (PesoCriterioInline,)


@admin.register(PesoCriterio)
class PesoCriterioAdmin(admin.ModelAdmin):
    list_display = (
        "conjunto",
        "criterio",
        "peso_local",
        "peso_global",
    )
    list_filter = ("conjunto", "criterio__bloque")
    search_fields = (
        "conjunto__nombre",
        "criterio__id_criterio",
        "criterio__nombre",
    )
    autocomplete_fields = ("conjunto", "criterio")
    ordering = ("conjunto", "criterio__id_criterio")
