import proj4 from 'proj4'
import type { SadeFeatureCollection } from '../types/api'

/** UTM Zone 13N — CRS de análisis SADE (backend). */
const EPSG_32613 =
  '+proj=utm +zone=13 +datum=WGS84 +units=m +no_defs +type=crs'
const EPSG_4326 = 'EPSG:4326'

proj4.defs('EPSG:32613', EPSG_32613)

function projectRing(ring: number[][]): number[][] {
  return ring.map(([x, y]) => {
    const [lon, lat] = proj4('EPSG:32613', EPSG_4326, [x, y])
    return [lon, lat]
  })
}

function looksLikeUtm(fc: SadeFeatureCollection): boolean {
  const crs = fc.sade_audit?.crs?.toUpperCase()
  if (crs?.includes('32613') || crs?.includes('UTM')) return true

  const first = fc.features[0]
  if (!first?.geometry) return false
  const coords =
    first.geometry.type === 'Polygon'
      ? first.geometry.coordinates[0]?.[0]
      : first.geometry.coordinates[0]?.[0]?.[0]
  if (!coords || coords.length < 2) return false
  const [a, b] = coords
  // WGS84 lon/lat stays within ~±180/±90; UTM easting/northing are large meters.
  return Math.abs(a) > 180 || Math.abs(b) > 90
}

/**
 * Reproyecta FeatureCollection de EPSG:32613 → WGS84 (EPSG:4326) para Leaflet+OSM.
 * Si ya parece WGS84, se devuelve sin cambios.
 */
export function toWgs84(fc: SadeFeatureCollection): SadeFeatureCollection {
  if (!looksLikeUtm(fc)) return fc

  const features = fc.features.map((feature) => {
    const geom = feature.geometry
    if (!geom) return feature

    if (geom.type === 'Polygon') {
      return {
        ...feature,
        geometry: {
          type: 'Polygon' as const,
          coordinates: geom.coordinates.map(projectRing),
        },
      }
    }

    if (geom.type === 'MultiPolygon') {
      return {
        ...feature,
        geometry: {
          type: 'MultiPolygon' as const,
          coordinates: geom.coordinates.map((poly) => poly.map(projectRing)),
        },
      }
    }

    return feature
  })

  return {
    ...fc,
    features,
    sade_audit: fc.sade_audit
      ? { ...fc.sade_audit, crs: 'EPSG:4326 (reproyectado desde EPSG:32613)' }
      : undefined,
  }
}
