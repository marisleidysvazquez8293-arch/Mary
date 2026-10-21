/** Seis clases de aptitud (alineadas con SuitabilityClass del backend CLP). */

export interface SuitabilityClassDef {
  code: number
  label: string
  /** Color de relleno en mapa y leyenda (contraste sobre OSM). */
  color: string
  /** Color de borde / texto sobre fondo claro. */
  stroke: string
}

export const SUITABILITY_CLASSES: readonly SuitabilityClassDef[] = [
  { code: 0, label: 'Excluido', color: '#4a5568', stroke: '#2d3748' },
  { code: 1, label: 'No apto', color: '#c53030', stroke: '#9b2c2c' },
  { code: 2, label: 'No recomendable', color: '#dd6b20', stroke: '#c05621' },
  { code: 3, label: 'Apto con restricciones', color: '#d69e2e', stroke: '#b7791e' },
  { code: 4, label: 'Favorable', color: '#38a169', stroke: '#2f855a' },
  { code: 5, label: 'Óptimo', color: '#276749', stroke: '#1c4532' },
] as const

export function colorForClass(code: number): string {
  return SUITABILITY_CLASSES.find((c) => c.code === code)?.color ?? '#718096'
}

export function labelForClass(code: number): string {
  return SUITABILITY_CLASSES.find((c) => c.code === code)?.label ?? `Clase ${code}`
}
