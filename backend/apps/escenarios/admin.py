from django.contrib import admin

from .models import Escenario


@admin.register(Escenario)
class EscenarioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "version_reglas_usada",
        "conjunto_pesos",
        "hash_configuracion",
        "hash_resultado",
        "fecha_ejecucion",
    )
    list_filter = ("version_reglas_usada", "fecha_ejecucion", "conjunto_pesos")
    search_fields = (
        "nombre",
        "hash_configuracion",
        "hash_resultado",
        "version_reglas_usada",
        "conjunto_pesos__nombre",
    )
    autocomplete_fields = ("conjunto_pesos",)
    readonly_fields = ()
    ordering = ("-fecha_ejecucion", "nombre")
