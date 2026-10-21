"""
Carga los 21 criterios de la Tabla 4.1 y pesos del Apéndice B (tesis SADE).

Uso:
    python manage.py load_initial_rules
    python manage.py load_initial_rules --dry-run

Idempotente: update_or_create por id_criterio / (criterio, version) / nombre AHP.

Distribución: GEO×7, ECO×4, SOC×10. Pesos y CR según Apéndice B (AIJ).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.reglas.data.initial_rules import (
    AHP_PROCEDENCIA,
    BLOQUE_WEIGHTS,
    CR_BLOQUES,
    CRITERIOS_SEED,
    DEFAULT_AHP_NOMBRE,
    DEFAULT_REGLA_VERSION,
)
from apps.reglas.models import Criterio, Regla


class Command(BaseCommand):
    help = (
        "Carga 21 criterios (Tabla 4.1: GEO×7, ECO×4, SOC×10), reglas v1.0.0 "
        "y ConjuntoPesosAHP del Apéndice B. Idempotente."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que se cargaría sin escribir en la BD.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run: no se escribirá en la BD."))

        created_c, updated_c = 0, 0
        created_r, updated_r = 0, 0

        for seed in CRITERIOS_SEED:
            defaults = {
                "nombre": seed["nombre"],
                "bloque": seed["bloque"],
                "fuente": seed["fuente"],
                "tipo_restriccion": seed["tipo_restriccion"],
                "activo": seed["activo"],
            }
            if dry_run:
                exists = Criterio.objects.filter(id_criterio=seed["id_criterio"]).exists()
                created_c += 0 if exists else 1
                updated_c += 1 if exists else 0
                criterio = None
            else:
                criterio, was_created = Criterio.objects.update_or_create(
                    id_criterio=seed["id_criterio"],
                    defaults=defaults,
                )
                if was_created:
                    created_c += 1
                else:
                    updated_c += 1

            regla_seed = seed["regla"]
            regla_defaults = {
                "parametros_json": regla_seed["parametros_json"],
                "es_regla_respaldo": bool(
                    regla_seed["parametros_json"].get("es_regla_respaldo_posible")
                ),
                "descripcion": regla_seed["descripcion"],
            }
            if dry_run:
                exists_r = Regla.objects.filter(
                    criterio__id_criterio=seed["id_criterio"],
                    version=DEFAULT_REGLA_VERSION,
                ).exists()
                created_r += 0 if exists_r else 1
                updated_r += 1 if exists_r else 0
            else:
                assert criterio is not None
                _, was_created_r = Regla.objects.update_or_create(
                    criterio=criterio,
                    version=DEFAULT_REGLA_VERSION,
                    defaults=regla_defaults,
                )
                if was_created_r:
                    created_r += 1
                else:
                    updated_r += 1

        ahp_defaults = {
            "descripcion": (
                "Pesos Apéndice B (tesis SADE). Panel 15 expertos; "
                f"agregación AIJ; procedencia={AHP_PROCEDENCIA}."
            ),
            "cr_geohidro": CR_BLOQUES["cr_geohidro"],
            "cr_ecol": CR_BLOQUES["cr_ecol"],
            "cr_socio": CR_BLOQUES["cr_socio"],
            "es_agregado_grupo": True,
        }

        if dry_run:
            ahp_exists = ConjuntoPesosAHP.objects.filter(nombre=DEFAULT_AHP_NOMBRE).exists()
            ahp_action = "update" if ahp_exists else "create"
            conjunto = None
        else:
            conjunto, ahp_created = ConjuntoPesosAHP.objects.update_or_create(
                nombre=DEFAULT_AHP_NOMBRE,
                defaults=ahp_defaults,
            )
            ahp_action = "create" if ahp_created else "update"

        pesos_created, pesos_updated = 0, 0
        for seed in CRITERIOS_SEED:
            cid = seed["id_criterio"]
            peso_local = float(seed["peso_local"])
            peso_global = float(seed["peso_global"])

            if dry_run:
                exists_p = PesoCriterio.objects.filter(
                    conjunto__nombre=DEFAULT_AHP_NOMBRE,
                    criterio__id_criterio=cid,
                ).exists()
                pesos_created += 0 if exists_p else 1
                pesos_updated += 1 if exists_p else 0
                continue

            assert conjunto is not None
            criterio_obj = Criterio.objects.get(id_criterio=cid)
            _, was_created_p = PesoCriterio.objects.update_or_create(
                conjunto=conjunto,
                criterio=criterio_obj,
                defaults={
                    "peso_local": peso_local,
                    "peso_global": peso_global,
                },
            )
            if was_created_p:
                pesos_created += 1
            else:
                pesos_updated += 1

        if dry_run:
            transaction.set_rollback(True)

        ids = ", ".join(s["id_criterio"] for s in CRITERIOS_SEED)
        n_geo = sum(1 for s in CRITERIOS_SEED if s["bloque"] == "geohidrologico")
        n_eco = sum(1 for s in CRITERIOS_SEED if s["bloque"] == "ecologico")
        n_soc = sum(1 for s in CRITERIOS_SEED if s["bloque"] == "socioeconomico")
        self.stdout.write(self.style.SUCCESS("load_initial_rules completado"))
        self.stdout.write(f"  Criterios: {created_c} creados, {updated_c} actualizados")
        self.stdout.write(
            f"  Distribución: GEO×{n_geo}, ECO×{n_eco}, SOC×{n_soc} (total {len(CRITERIOS_SEED)})"
        )
        self.stdout.write(
            f"  Reglas v{DEFAULT_REGLA_VERSION}: {created_r} creadas, {updated_r} actualizadas"
        )
        self.stdout.write(f"  ConjuntoPesosAHP '{DEFAULT_AHP_NOMBRE}': {ahp_action}")
        self.stdout.write(f"  PesoCriterio: {pesos_created} creados, {pesos_updated} actualizados")
        self.stdout.write(
            f"  Pesos bloque: GEO={BLOQUE_WEIGHTS['geohidrologico']:.2%} "
            f"ECO={BLOQUE_WEIGHTS['ecologico']:.2%} "
            f"SOC={BLOQUE_WEIGHTS['socioeconomico']:.2%}"
        )
        self.stdout.write(
            f"  CR: geo={CR_BLOQUES['cr_geohidro']}, "
            f"eco={CR_BLOQUES['cr_ecol']}, socio={CR_BLOQUES['cr_socio']}"
        )
        self.stdout.write(f"  IDs: {ids}")
