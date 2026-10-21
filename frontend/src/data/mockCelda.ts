import { BLOQUE_LABEL, CRITERIOS_21 } from '../constants/criterios'
import { labelForClass } from '../constants/suitability'
import type { ConsultaCeldaResponse, FactorCelda } from '../types/api'

/** Pesos globales demo (≈ Tabla 4.1; no son los finales del Apéndice B). */
const PESOS_DEMO: Record<string, number> = {
  GEO_01: 0.062, GEO_02: 0.055, GEO_03: 0.05, GEO_04: 0.048,
  GEO_05: 0.045, GEO_06: 0.052, GEO_07: 0.0535,
  ECO_01: 0.09, ECO_02: 0.08, ECO_03: 0.07, ECO_04: 0.0701,
  SOC_01: 0.028, SOC_02: 0.045, SOC_03: 0.035, SOC_04: 0.032,
  SOC_05: 0.025, SOC_06: 0.04, SOC_07: 0.03, SOC_08: 0.028,
  SOC_09: 0.03, SOC_10: 0.0314,
}

function hashCoord(lat: number, lon: number): number {
  const x = Math.sin(lat * 12.9898 + lon * 78.233) * 43758.5453
  return x - Math.floor(x)
}

/**
 * Desglose mock de 21 factores + advertencia aeródromo (NOM-083 6.1.1).
 * Usado cuando GET …/celda/ no está disponible.
 */
export function buildMockCelda(
  escenarioId: number,
  lat: number,
  lon: number,
): ConsultaCeldaResponse {
  const seed = hashCoord(lat, lon)
  const nearAirport = seed > 0.55

  const factores: FactorCelda[] = CRITERIOS_21.map((c, i) => {
    const local = (seed * (i + 3)) % 1
    const restriccion = c.esRestriccionNormativa && local < 0.08 && c.id !== 'SOC_01'
    const valor = restriccion ? 0 : 1 + local * 4
    const peso = PESOS_DEMO[c.id] ?? 1 / 21
    return {
      id_criterio: c.id,
      nombre: c.nombre,
      bloque: BLOQUE_LABEL[c.bloque],
      valor_factor: Number(valor.toFixed(2)),
      peso,
      contribucion: Number((valor * peso).toFixed(4)),
      restriccion_activa: restriccion,
      detalle: restriccion
        ? 'Restricción activa (cⱼ = 0)'
        : c.id === 'SOC_01' && nearAirport
          ? 'Dentro de 13 km — advertencia aviaria (no excluye)'
          : undefined,
    }
  })

  const excluido = factores.some((f) => f.restriccion_activa)
  const S = excluido
    ? 0
    : factores.reduce((acc, f) => acc + f.contribucion, 0)
  // Escala demo 0–5 → class_code aproximado
  let class_code = 5
  if (excluido || S <= 1e-9) class_code = 0
  else if (S <= 1.5) class_code = 1
  else if (S <= 2.5) class_code = 2
  else if (S <= 3.5) class_code = 3
  else if (S <= 4.5) class_code = 4

  const restricciones = factores
    .filter((f) => f.restriccion_activa)
    .map((f) => `${f.id_criterio}: ${f.nombre}`)

  const advertencias: string[] = []
  if (nearAirport) {
    advertencias.push(
      'Requiere estudio de riesgo aviario (NOM-083, numeral 6.1.1).',
    )
  }

  return {
    escenario_id: escenarioId,
    lat,
    lon,
    class_code,
    class_label: labelForClass(class_code),
    suitability: Number(S.toFixed(3)),
    excluido,
    factores,
    restricciones,
    advertencias,
    advertencia_aerodromo: {
      aplica: nearAirport,
      distancia_km: nearAirport ? Number((8 + seed * 5).toFixed(1)) : undefined,
      mensaje: nearAirport
        ? 'Celda a menos de 13 km del centro de pista: no se excluye, pero exige estudio de riesgo aviario.'
        : 'Fuera del radio de 13 km a aeródromo.',
    },
    fuente: 'mock',
  }
}
