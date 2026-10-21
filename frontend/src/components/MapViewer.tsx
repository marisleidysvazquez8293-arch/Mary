import { useEffect, useMemo } from 'react'
import {
  GeoJSON,
  MapContainer,
  TileLayer,
  useMap,
  useMapEvents,
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

export interface MapClickPayload {
  lat: number
  lon: number
}

interface MapViewerProps {
  geojson: SadeFeatureCollection | null
  fitKey: string | number | null
  onMapClick?: (p: MapClickPayload) => void
  clickMarker?: MapClickPayload | null
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

function ClickHandler({ onMapClick }: { onMapClick?: (p: MapClickPayload) => void }) {
  useMapEvents({
    click(e) {
      onMapClick?.({ lat: e.latlng.lat, lon: e.latlng.lng })
    },
  })
  return null
}

function ClickMarker({ point }: { point: MapClickPayload | null | undefined }) {
  const map = useMap()
  useEffect(() => {
    if (!point) return
    const m = L.circleMarker([point.lat, point.lon], {
      radius: 7,
      color: '#1e293b',
      weight: 2,
      fillColor: '#f8fafc',
      fillOpacity: 0.95,
    }).addTo(map)
    m.bindTooltip('Consulta de celda', { direction: 'top', offset: [0, -6] })
    return () => {
      map.removeLayer(m)
    }
  }, [map, point])
  return null
}

function splitLayers(fc: FeatureCollection | null): {
  exclusion: FeatureCollection | null
  aptitude: FeatureCollection | null
} {
  if (!fc?.features?.length) return { exclusion: null, aptitude: null }
  const excl: Feature[] = []
  const apt: Feature[] = []
  for (const f of fc.features) {
    const code = Number(f.properties?.class_code ?? -1)
    if (code === 0 || f.properties?.excluded === true) excl.push(f)
    else apt.push(f)
  }
  return {
    exclusion: excl.length
      ? { type: 'FeatureCollection', features: excl }
      : null,
    aptitude: apt.length ? { type: 'FeatureCollection', features: apt } : null,
  }
}

function styleAptitude(feature?: Feature<Geometry>): PathOptions {
  const code = Number(feature?.properties?.class_code ?? -1)
  return {
    fillColor: colorForClass(code),
    fillOpacity: 0.7,
    color: '#1a202c',
    weight: 0.5,
    opacity: 0.8,
  }
}

function styleExclusion(): PathOptions {
  return {
    fillColor: '#2d3748',
    fillOpacity: 0.55,
    color: '#0f172a',
    weight: 1,
    opacity: 0.95,
    dashArray: '4 3',
  }
}

function bindPopup(feature: Feature<Geometry>, layer: L.Layer) {
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
    `<strong>${label}</strong><br/>Código: ${props.class_code ?? '—'}<br/>Aptitud: ${suit}<br/><em>Clic en el mapa para desglose de celda</em>`,
  )
}

export function MapViewer({
  geojson,
  fitKey,
  onMapClick,
  clickMarker,
}: MapViewerProps) {
  const wgs84 = useMemo(
    () => (geojson ? toWgs84(geojson) : null),
    [geojson],
  )
  const leafletData = wgs84 as FeatureCollection | null
  const { exclusion, aptitude } = useMemo(
    () => splitLayers(leafletData),
    [leafletData],
  )

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
        <ClickHandler onMapClick={onMapClick} />
        <ClickMarker point={clickMarker} />
        {aptitude && (
          <GeoJSON
            key={`apt-${String(fitKey)}`}
            data={aptitude}
            style={styleAptitude}
            onEachFeature={bindPopup}
          />
        )}
        {exclusion && (
          <GeoJSON
            key={`exc-${String(fitKey)}`}
            data={exclusion}
            style={styleExclusion}
            onEachFeature={bindPopup}
          />
        )}
      </MapContainer>
      <Legend />
      <p className="map-hint">Clic en el mapa → consulta de celda (21 factores)</p>
    </div>
  )
}
