"""
Load SADE initial criteria, default rules, and AHP weights (PASO 2).

Usage:
    python manage.py load_initial_rules
    python manage.py load_initial_rules --dry-run

Idempotent: safe to re-run. Uses update_or_create keyed by id_criterio /
(criterio, version) / conjunto nombre + criterio.

PLACEHOLDER PENDING THESIS PDF:
  Tabla 4.1 and Apéndice B are not in the repository. Seed data in
  apps.reglas.data.initial_rules is a NOM-083-aligned placeholder set of
  21 ids (GEO_01–07, ECO_01–07, SOC_01–07). Replace with thesis values when
  available. Block weights 36.54 / 31.01 / 32.45% come from the PASO 2 brief
  (Apéndice B). CR fields are 0.0 until AHPService (PASO 3+) computes them.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.multicriterio.models import ConjuntoPesosAHP, PesoCriterio
from apps.reglas.data.initial_rules import (
    BLOQUE_WEIGHTS,
    CRITERIOS_SEED,
    DEFAULT_AHP_NOMBRE,
    DEFAULT_REGLA_VERSION,
    PESOS_LOCALES,
)
from apps.reglas.models import Criterio, Regla


class Command(BaseCommand):
    help = (
        "Carga 21 criterios (Tabla 4.1 placeholder), reglas v1.0.0 y "
        "ConjuntoPesosAHP default (Apéndice B). Idempotente."
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
                if exists:
                    updated_c += 1
                else:
                    created_c += 1
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
                "es_regla_respaldo": False,
                "descripcion": regla_seed["descripcion"],
            }
            if dry_run:
                if criterio is None:
                    # Approximate: treat as create if criterio would be new
                    pass
                exists_r = Regla.objects.filter(
                    criterio__id_criterio=seed["id_criterio"],
                    version=DEFAULT_REGLA_VERSION,
                ).exists()
                if exists_r:
                    updated_r += 1
                else:
                    created_r += 1
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

        # --- AHP default conjunto ---
        # CR left at 0.0: real consistency ratios come from AHPService later.
        ahp_defaults = {
            "descripcion": (
                "Pesos por bloque Apéndice B (placeholder pending thesis PDF). "
                "CR=0 hasta AHPService."
            ),
            "cr_geohidro": 0.0,
            "cr_ecol": 0.0,
            "cr_socio": 0.0,
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
            bloque = seed["bloque"]
            peso_local = PESOS_LOCALES[cid]
            peso_global = peso_local * BLOQUE_WEIGHTS[bloque]

            if dry_run:
                exists_p = PesoCriterio.objects.filter(
                    conjunto__nombre=DEFAULT_AHP_NOMBRE,
                    criterio__id_criterio=cid,
                ).exists()
                if exists_p:
                    pesos_updated += 1
                else:
                    pesos_created += 1
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
            # Roll back any accidental writes (none expected) and abort transaction
            transaction.set_rollback(True)

        ids = ", ".join(s["id_criterio"] for s in CRITERIOS_SEED)
        self.stdout.write(self.style.SUCCESS("load_initial_rules completed"))
        self.stdout.write(f"  Criterios: {created_c} created, {updated_c} updated")
        self.stdout.write(f"  Reglas v{DEFAULT_REGLA_VERSION}: {created_r} created, {updated_r} updated")
        self.stdout.write(f"  ConjuntoPesosAHP '{DEFAULT_AHP_NOMBRE}': {ahp_action}")
        self.stdout.write(f"  PesoCriterio: {pesos_created} created, {pesos_updated} updated")
        self.stdout.write(
            f"  Block weights: GEO={BLOQUE_WEIGHTS['geohidrologico']:.2%} "
            f"ECO={BLOQUE_WEIGHTS['ecologico']:.2%} "
            f"SOC={BLOQUE_WEIGHTS['socioeconomico']:.2%}"
        )
        self.stdout.write(f"  IDs ({len(CRITERIOS_SEED)}): {ids}")
        self.stdout.write(
            self.style.WARNING(
                "  NOTE: placeholder pending thesis PDF (Tabla 4.1 / Apéndice B). "
                "CR fields are 0.0 until AHPService."
            )
        )
