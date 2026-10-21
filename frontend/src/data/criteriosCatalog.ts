/** Catálogo Tabla 4.1 + pesos Apéndice B (seed backend initial_rules). */

export type BloqueCriterio = 'geohidrologico' | 'ecologico' | 'socioeconomico'
export type TipoRestriccion = 'normativa' | 'modelo' | 'advertencia'

export interface CriterioCatalogo {
  id: string
  nombre: string
  bloque: BloqueCriterio
  tipo_restriccion: TipoRestriccion
  peso_global: number
  /** Buffer NOM-083 / SEDESOL (m). Bloqueado para usuarios normales si normativa. */
  buffer_m: number | null
  buffer_bloqueado: boolean
  norma?: string
  version: string
}

export const BLOQUE_LABEL: Record<BloqueCriterio, string> = {
  geohidrologico: 'Geohidrológico',
  ecologico: 'Ecológico',
  socioeconomico: 'Socioeconómico',
}

export const BLOQUE_WEIGHTS = {
  geohidrologico: 0.3654,
  ecologico: 0.3101,
  socioeconomico: 0.3245,
} as const

export const CR_BLOQUES = {
  cr_geohidro: 0.0035,
  cr_ecol: 0.002,
  cr_socio: 0.0047,
  cr_criterios: 0.002,
} as const

export const AHP_PROCEDENCIA = {
  panel: 15,
  fechas: '2026-04-17 a 2026-05-07',
  metodo: 'AIJ media geométrica',
  nombre: 'AHP Apéndice B — panel 15 expertos (AIJ)',
}

/** Buffers NOM-083 bloqueados a edición por usuarios normales. */
export const CRITERIOS_CATALOGO: CriterioCatalogo[] = [
  { id: 'GEO_01', nombre: 'Zonas de recarga de acuíferos', bloque: 'geohidrologico', tipo_restriccion: 'normativa', peso_global: 0.0516, buffer_m: 1000, buffer_bloqueado: true, norma: 'NOM-083 §6.1.4', version: '1.0.0' },
  { id: 'GEO_02', nombre: 'Zona de inundación (T=100 años)', bloque: 'geohidrologico', tipo_restriccion: 'normativa', peso_global: 0.0546, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083 §6.1.5', version: '1.0.0' },
  { id: 'GEO_03', nombre: 'Fracturas o fallas geológicas', bloque: 'geohidrologico', tipo_restriccion: 'normativa', peso_global: 0.0528, buffer_m: 500, buffer_bloqueado: true, norma: 'NOM-083 §6.1.4', version: '1.0.0' },
  { id: 'GEO_04', nombre: 'Zonas de riesgo de deslizamiento', bloque: 'geohidrologico', tipo_restriccion: 'modelo', peso_global: 0.056, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'GEO_05', nombre: 'Cavernas', bloque: 'geohidrologico', tipo_restriccion: 'normativa', peso_global: 0.0468, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083 §6.1.4', version: '1.0.0' },
  { id: 'GEO_06', nombre: 'Planicies aluviales', bloque: 'geohidrologico', tipo_restriccion: 'normativa', peso_global: 0.0502, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083 §6.1.4', version: '1.0.0' },
  { id: 'GEO_07', nombre: 'Tipo de suelo', bloque: 'geohidrologico', tipo_restriccion: 'modelo', peso_global: 0.0534, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'ECO_01', nombre: 'Cuerpos de agua superficial', bloque: 'ecologico', tipo_restriccion: 'normativa', peso_global: 0.0876, buffer_m: 500, buffer_bloqueado: true, norma: 'NOM-083 §6.1.6', version: '1.0.0' },
  { id: 'ECO_02', nombre: 'Pozos de extracción de agua', bloque: 'ecologico', tipo_restriccion: 'normativa', peso_global: 0.0747, buffer_m: 500, buffer_bloqueado: true, norma: 'NOM-083 §6.1.7', version: '1.0.0' },
  { id: 'ECO_03', nombre: 'Ecosistemas acuáticos', bloque: 'ecologico', tipo_restriccion: 'normativa', peso_global: 0.0767, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083', version: '1.0.0' },
  { id: 'ECO_04', nombre: 'Áreas naturales protegidas', bloque: 'ecologico', tipo_restriccion: 'normativa', peso_global: 0.0712, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083 §6.1.2', version: '1.0.0' },
  { id: 'SOC_01', nombre: 'Distancia a aeródromos (13 km)', bloque: 'socioeconomico', tipo_restriccion: 'advertencia', peso_global: 0.034, buffer_m: 13000, buffer_bloqueado: true, norma: 'NOM-083 §6.1.1', version: '1.0.0' },
  { id: 'SOC_02', nombre: 'Proximidad a localidades > 2 500 hab.', bloque: 'socioeconomico', tipo_restriccion: 'normativa', peso_global: 0.0325, buffer_m: 500, buffer_bloqueado: true, norma: 'NOM-083 §6.1.3', version: '1.0.0' },
  { id: 'SOC_03', nombre: 'Vías de acceso', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0336, buffer_m: 200, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_04', nombre: 'Uso de suelo', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0321, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_05', nombre: 'Facilidad de compra del terreno', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.034, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_06', nombre: 'Zonas arqueológicas', bloque: 'socioeconomico', tipo_restriccion: 'normativa', peso_global: 0.0342, buffer_m: null, buffer_bloqueado: true, norma: 'NOM-083 §6.1.4', version: '1.0.0' },
  { id: 'SOC_07', nombre: 'Vida útil del sitio', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0335, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_08', nombre: 'Material de cobertura', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0323, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_09', nombre: 'Líneas de alta tensión', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0279, buffer_m: 50, buffer_bloqueado: false, version: '1.0.0' },
  { id: 'SOC_10', nombre: 'Intermunicipalidad', bloque: 'socioeconomico', tipo_restriccion: 'modelo', peso_global: 0.0303, buffer_m: null, buffer_bloqueado: false, version: '1.0.0' },
]

export const VERSIONES_REGLAS = ['1.0.0', '1.1.0-demo'] as const

/** Leyenda legal del expediente (RF-039). */
export const LEYENDA_LEGAL = `Este expediente documenta un escenario de evaluación multicriterio del Sistema de Apoyo a Decisiones Espaciales (SADE) para la localización de sitios de disposición final de residuos sólidos urbanos en la región Valles de Jalisco. Los criterios se fundamentan en la NOM-083-SEMARNAT-2003 y antecedentes técnicos (SEDESOL, EPA, OPS). Los pesos AHP proceden del Apéndice B (panel de 15 expertos, agregación AIJ). El resultado no sustituye los estudios de sitio, permisos ni dictámenes que exija la autoridad competente.`
