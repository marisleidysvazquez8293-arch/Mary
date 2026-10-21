import type { LatLngBoundsExpression, LatLngExpression } from 'leaflet'

/**
 * Región de estudio: Valles de Jalisco (aprox. Ameca–Tequila–Ahualulco).
 * Usado para zoom inicial del visor.
 */
export const VALLES_CENTER: LatLngExpression = [20.62, -103.95]

/** Bounds aproximados [SW, NE] en WGS84. */
export const VALLES_BOUNDS: LatLngBoundsExpression = [
  [20.25, -104.45],
  [21.05, -103.35],
]

export const DEFAULT_ZOOM = 10
