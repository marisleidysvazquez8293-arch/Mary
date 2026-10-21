"""
PdfExpedienteService — expediente técnico PDF (RF-046 / PASO 4).

ReportLab. Leyenda legal exacta de la tesis / requisitos VIS.
"""
from __future__ import annotations

import io
from typing import Any

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.escenarios.models import Escenario
from apps.escenarios.services.traceability import (
    SADE_SOFTWARE_VERSION,
    ScenarioTraceabilityService,
)
from apps.multicriterio.models import PesoCriterio
from apps.reglas.data.initial_rules import (
    AHP_PROCEDENCIA,
    CRITERIOS_SEED,
    DEFAULT_REGLA_VERSION,
)
from apps.reglas.models import Criterio, Regla

LEYENDA_LEGAL = (
    "Documento de apoyo a la toma de decisiones; no constituye una "
    "recomendación vinculante de sitio ni sustituye los estudios de "
    "impacto ambiental normativos"
)

CELL_AREA_HA_DEFAULT = 1.0  # demo: 100 m × 100 m = 1 ha si cell_area_m2=10000


class PdfExpedienteService:
    """Genera el PDF de expediente técnico de un escenario."""

    def generar_pdf_expediente(self, escenario_id: int) -> bytes:
        escenario = Escenario.objects.select_related("conjunto_pesos").get(
            pk=escenario_id
        )
        trace = ScenarioTraceabilityService()
        hash_cfg = escenario.hash_configuracion or trace.generar_hash_configuracion(
            escenario
        )
        hash_trz = trace.generar_hash_configuracion(escenario)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=1.8 * cm,
            rightMargin=1.8 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title=f"Expediente SADE — {escenario.nombre}",
            # Metadatos sin comprimir (auditoría / tests)
            subject=f"hash={hash_cfg} | {LEYENDA_LEGAL}",
            creator="SADE Valles de Jalisco",
            keywords=f"SADE,{hash_cfg},relleno sanitario",
        )
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="SadeTitle",
                parent=styles["Heading1"],
                alignment=TA_CENTER,
                fontSize=14,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SadeLegal",
                parent=styles["Normal"],
                alignment=TA_JUSTIFY,
                fontSize=9,
                textColor=colors.HexColor("#333333"),
                leading=12,
                spaceBefore=12,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SadeSmall",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
            )
        )

        story: list[Any] = []
        story.append(
            Paragraph(
                "SADE — Sistema de apoyo a la decisión espacial<br/>"
                "Localización de rellenos sanitarios · Región Valles de Jalisco",
                styles["SadeTitle"],
            )
        )
        story.append(
            Paragraph(
                f"<b>Expediente técnico del escenario</b>: {escenario.nombre}",
                styles["Heading2"],
            )
        )
        story.append(
            Paragraph(
                f"ID escenario: {escenario.pk}<br/>"
                f"Versión reglas: {escenario.version_reglas_usada or DEFAULT_REGLA_VERSION}<br/>"
                f"Software SADE: {getattr(settings, 'SADE_SOFTWARE_VERSION', SADE_SOFTWARE_VERSION)}<br/>"
                f"CRS análisis: EPSG:32613<br/>"
                f"<b>Hash configuración</b>: {hash_cfg}<br/>"
                f"Hash trazabilidad: {hash_trz}<br/>"
                f"Hash resultado: {escenario.hash_resultado or '—'}<br/>"
                f"Fecha ejecución: {escenario.fecha_ejecucion or '—'}",
                styles["SadeSmall"],
            )
        )
        story.append(Spacer(1, 0.4 * cm))

        # --- 21 criterios / umbrales ---
        story.append(Paragraph("1. Criterios y umbrales (21)", styles["Heading2"]))
        crit_rows = [["ID", "Nombre", "Bloque", "Tipo", "Umbrales / parámetros"]]
        criterios = {c.id_criterio: c for c in Criterio.objects.all()}
        for seed in CRITERIOS_SEED:
            cid = seed["id_criterio"]
            crit = criterios.get(cid)
            regla = None
            if crit:
                regla = (
                    Regla.objects.filter(criterio=crit)
                    .order_by("-id")
                    .first()
                )
            params = {}
            if regla and regla.parametros_json:
                params = regla.parametros_json
            else:
                params = seed.get("regla", {}).get("parametros_json", {})
            umbral_txt = ", ".join(f"{k}={v}" for k, v in list(params.items())[:4])
            if len(umbral_txt) > 42:
                umbral_txt = umbral_txt[:39] + "…"
            crit_rows.append(
                [
                    cid,
                    (seed["nombre"][:28] + "…")
                    if len(seed["nombre"]) > 28
                    else seed["nombre"],
                    seed["bloque"][:8],
                    seed["tipo_restriccion"][:10],
                    umbral_txt or "—",
                ]
            )
        t = Table(crit_rows, colWidths=[1.4 * cm, 5.2 * cm, 2.0 * cm, 2.0 * cm, 5.5 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4d3e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f3f6f4")],
                    ),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.35 * cm))

        # --- CR AHP y procedencia ---
        story.append(
            Paragraph("2. CR AHP y procedencia de los pesos", styles["Heading2"])
        )
        cj = escenario.conjunto_pesos
        proc = AHP_PROCEDENCIA
        story.append(
            Paragraph(
                f"Conjunto: <b>{cj.nombre}</b><br/>"
                f"CR geohidrológico: {cj.cr_geohidro} · "
                f"CR ecológico: {cj.cr_ecol} · "
                f"CR socioeconómico: {cj.cr_socio}<br/>"
                f"Agregado de grupo (AIJ): {'sí' if cj.es_agregado_grupo else 'no'}<br/>"
                f"Panel: {proc.get('panel')} expertos · "
                f"Fechas: {proc.get('fechas')}<br/>"
                f"Método: {proc.get('metodo_agregacion')}<br/>"
                f"CR criterios principales: {proc.get('cr_criterios_principales')}",
                styles["SadeSmall"],
            )
        )
        peso_rows = [["ID", "Peso local", "Peso global"]]
        for p in (
            PesoCriterio.objects.filter(conjunto=cj)
            .select_related("criterio")
            .order_by("criterio__id_criterio")
        ):
            peso_rows.append(
                [
                    p.criterio.id_criterio,
                    f"{p.peso_local:.4f}",
                    f"{p.peso_global:.4f}",
                ]
            )
        if len(peso_rows) == 1:
            for seed in CRITERIOS_SEED:
                peso_rows.append(
                    [
                        seed["id_criterio"],
                        f"{seed['peso_local']:.4f}",
                        f"{seed['peso_global']:.4f}",
                    ]
                )
        tp = Table(peso_rows, colWidths=[2.5 * cm, 3 * cm, 3 * cm])
        tp.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4d3e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ]
            )
        )
        story.append(Spacer(1, 0.2 * cm))
        story.append(tp)
        story.append(Spacer(1, 0.35 * cm))

        # --- Superficies ---
        story.append(
            Paragraph("3. Superficies por clase de aptitud", styles["Heading2"])
        )
        counts = (escenario.resultados_json or {}).get("class_counts") or {}
        cell_area_m2 = float(
            (escenario.parametros_ejecucion or {}).get("cell_area_m2", 10_000.0)
        )
        ha_per_cell = cell_area_m2 / 10_000.0
        total_cells = sum(int(v) for v in counts.values()) or 1
        surf_rows = [["Clase", "Celdas", "Superficie (ha)", "%"]]
        for label, n in counts.items():
            n_i = int(n)
            ha = n_i * ha_per_cell
            pct = 100.0 * n_i / total_cells
            surf_rows.append([str(label), str(n_i), f"{ha:.2f}", f"{pct:.1f}%"])
        ts = Table(surf_rows, colWidths=[5 * cm, 2.5 * cm, 3.5 * cm, 2.5 * cm])
        ts.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4d3e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ]
            )
        )
        story.append(ts)
        story.append(Spacer(1, 0.6 * cm))

        # --- Leyenda legal exacta ---
        story.append(Paragraph("4. Aviso legal", styles["Heading2"]))
        story.append(Paragraph(LEYENDA_LEGAL, styles["SadeLegal"]))

        doc.build(story)
        return buf.getvalue()
