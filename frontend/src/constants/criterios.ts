/** Reexporta catálogo para compatibilidad con mockCelda y paneles. */
export {
  BLOQUE_LABEL,
  CRITERIOS_CATALOGO,
  VERSIONES_REGLAS,
  type BloqueCriterio,
} from '../data/criteriosCatalog'
import { CRITERIOS_CATALOGO, type BloqueCriterio } from '../data/criteriosCatalog'

export interface CriterioDef {
  id: string
  nombre: string
  bloque: BloqueCriterio
  esRestriccionNormativa: boolean
}

export const CRITERIOS_21: readonly CriterioDef[] = CRITERIOS_CATALOGO.map((c) => ({
  id: c.id,
  nombre: c.nombre,
  bloque: c.bloque,
  esRestriccionNormativa: c.tipo_restriccion === 'normativa' || c.tipo_restriccion === 'advertencia',
}))
