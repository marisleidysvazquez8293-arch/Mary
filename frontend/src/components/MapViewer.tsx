import { useEffect, useMemo } from 'react'
import {
  GeoJSON,
  MapContainer,
  TileLayer,
  useMap,
  ZoomControl,
} from 'react-leaflet'
import type { Feature, FeatureCollection, Geometry } from 'geojson'
import type { PathOptions } from 'leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import { DEFAULT_ZOOM, VALLES_BOUNDS, VALLES_CENTER } from '../constants/region'
import { colorForClass, labelForClass } from '../constants/suitability'
import type { SadeFeatureCollection } from '../types/api'
import { toWgs84 } from '../utils/reproject'
import { Legend } from './Legend'

interface MapViewerProps {
  geojson: SadeFeatureCollection | null
  fitKey: string | number | null
}

function FitToData({
  data,
  fitKey,
}: {
  data: FeatureCollection | null
  fitKey: string | number | null
}) {
  const map = useMap()

  useEffect(() => {
    if (!data?.features?.length) {
      map.fitBounds(VALLES_BOUNDS, { padding: [24, 24] })
      return
    }
    const layer = L.geoJSON(data as GeoJSON.GeoJsonObject)
    const bounds = layer.getBounds()
    if (bounds.isValid()) {
      map.fitBounds(bounds.pad(0.08), { maxZoom: 13 })
    } else {
      map.fitBounds(VALLES_BOUNDS, { padding: [24, 24] })
    }
  }, [map, data, fitKey])

  return null
}

function styleFeature(feature?: Feature<Geometry>): PathOptions {
  const code = Number(feature?.properties?.class_code ?? -1)
  return {
    fillColor: colorForClass(code),
    fillOpacity: 0.72,
    color: '#1a202c',
    weight: 0.6,
    opacity: 0.85,
  }
}

function onEachFeature(feature: Feature<Geometry>, layer: L.Layer) {
  const props = feature.properties as {
    class_code?: number
    class_label?: string
    suitability?: number
  } | null
  if (!props) return
  const label = props.class_label ?? labelForClass(Number(props.class_code))
  const suit =
    typeof props.suitability === 'number' ? props.suitability.toFixed(3) : '—'
  layer.bindPopup(
    `<strong>${label}</strong><br/>Código: ${props.class_code ?? '—'}<br/>Aptitud S: ${suit}`,
  )
}

export function MapViewer({ geojson, fitKey }: MapViewerProps) {
  const wgs84 = useMemo(
    () => (geojson ? toWgs84(geojson) : null),
    [geojson],
  )

  const leafletData = wgs84 as FeatureCollection | null

  return (
    <div className="map-shell">
      <MapContainer
        center={VALLES_CENTER}
        zoom={DEFAULT_ZOOM}
        className="map-shell__map"
        zoomControl={false}
        preferCanvas
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="topright" />
        <FitToData data={leafletData} fitKey={fitKey} />
        {leafletData && (
          <GeoJSON
            key={String(fitKey)}
            data={leafletData}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>
      <Legend />
    </div>
  )
}
