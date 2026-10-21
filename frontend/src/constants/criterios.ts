/** Catálogo de 21 criterios (Tabla 4.1 / tesis). Códigos alineados al seed backend. */

export type BloqueCriterio = 'geohidrologico' | 'ecologico' | 'socioeconomico'

export interface CriterioDef {
  id: string
  nombre: string
  bloque: BloqueCriterio
  /** Si es restricción normativa NOM-083 (no desactivable). */
  esRestriccionNormativa: boolean
}

export const CRITERIOS_21: readonly CriterioDef[] = [
  { id: 'GEO_01', nombre: 'Zonas de recarga de acuíferos', bloque: 'geohidrologico', esRestriccionNormativa: true },
  { id: 'GEO_02', nombre: 'Zonas de inundación (T=100 años)', bloque: 'geohidrologico', esRestriccionNormativa: true },
  { id: 'GEO_03', nombre: 'Fracturas o fallas geológicas', bloque: 'geohidrologico', esRestriccionNormativa: true },
  { id: 'GEO_04', nombre: 'Riesgo de deslizamiento', bloque: 'geohidrologico', esRestriccionNormativa: false },
  { id: 'GEO_05', nombre: 'Cavernas', bloque: 'geohidrologico', esRestriccionNormativa: true },
  { id: 'GEO_06', nombre: 'Planicies aluviales', bloque: 'geohidrologico', esRestriccionNormativa: false },
  { id: 'GEO_07', nombre: 'Tipo de suelo', bloque: 'geohidrologico', esRestriccionNormativa: false },
  { id: 'ECO_01', nombre: 'Cuerpos de agua superficial', bloque: 'ecologico', esRestriccionNormativa: true },
  { id: 'ECO_02', nombre: 'Pozos de extracción de agua', bloque: 'ecologico', esRestriccionNormativa: true },
  { id: 'ECO_03', nombre: 'Ecosistemas acuáticos', bloque: 'ecologico', esRestriccionNormativa: true },
  { id: 'ECO_04', nombre: 'Áreas naturales protegidas', bloque: 'ecologico', esRestriccionNormativa: true },
  { id: 'SOC_01', nombre: 'Distancia a aeródromos (13 km)', bloque: 'socioeconomico', esRestriccionNormativa: true },
  { id: 'SOC_02', nombre: 'Proximidad a localidades > 2 500 hab.', bloque: 'socioeconomico', esRestriccionNormativa: true },
  { id: 'SOC_03', nombre: 'Vías de acceso', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_04', nombre: 'Uso de suelo', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_05', nombre: 'Facilidad de compra del terreno', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_06', nombre: 'Zonas arqueológicas', bloque: 'socioeconomico', esRestriccionNormativa: true },
  { id: 'SOC_07', nombre: 'Vida útil del sitio', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_08', nombre: 'Material de cobertura', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_09', nombre: 'Líneas de alta tensión', bloque: 'socioeconomico', esRestriccionNormativa: false },
  { id: 'SOC_10', nombre: 'Intermunicipalidad', bloque: 'socioeconomico', esRestriccionNormativa: false },
] as const

export const BLOQUE_LABEL: Record<BloqueCriterio, string> = {
  geohidrologico: 'Geohidrológico',
  ecologico: 'Ecológico',
  socioeconomico: 'Socioeconómico',
}

export const VERSIONES_REGLAS = ['1.0.0', '1.1.0-demo'] as const
