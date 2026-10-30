import { useEffect, useRef, useState } from 'react'
import type { FeatureCollection } from 'geojson'
import L, { type Map as LeafletMap } from 'leaflet'
import { Circle, GeoJSON, MapContainer, Rectangle, TileLayer, Tooltip, useMap, useMapEvents } from 'react-leaflet'
import type { LayerId, MapFeature } from '../data'
import { allFeatures, displayName, layerMeta } from '../data'
import { createPopupContent } from '../popup'
import { extentOf, pointLatLng, PROXIMITY_RADIUS_METERS } from '../spatial'

const studyBounds = L.latLngBounds(extentOf(allFeatures.map(({ feature }) => feature)))
const initialBounds = studyBounds.pad(0.16)
const explorationBounds = studyBounds.pad(2.4)

type Props = {
  features: Record<LayerId, MapFeature[]>
  selectedId: number | null
}

function UrlState() {
  useMapEvents({
    moveend(event) {
      const map = event.target
      const center = map.getCenter()
      const params = new URLSearchParams(window.location.search)
      params.set('lat', center.lat.toFixed(5))
      params.set('lng', center.lng.toFixed(5))
      params.set('z', String(map.getZoom()))
      history.replaceState(null, '', `${window.location.pathname}?${params}#mapa`)
    },
  })
  return null
}

function ResetView() {
  const map = useMap()
  return <button className="map-action map-action--reset" onClick={() => map.fitBounds(initialBounds, { padding: [24, 24] })} title="voltar ao enquadramento inicial">⌂ <span>reenquadrar</span></button>
}

function Selection({ id, refs }: { id: number | null; refs: React.RefObject<Record<number, L.Layer>> }) {
  const map = useMap()
  useEffect(() => {
    if (id === null) return
    const layer = refs.current[id]
    if (!layer) return
    const target = layer as L.Marker & { getBounds?: () => L.LatLngBounds }
    if (target.getBounds) map.fitBounds(target.getBounds(), { maxZoom: 17, padding: [80, 80] })
    else if (target.getLatLng) map.setView(target.getLatLng(), 17)
    target.openPopup()
  }, [id, map, refs])
  return null
}

export function MapView({ features, selectedId }: Props) {
  const mapRef = useRef<LeafletMap>(null)
  const layerRefs = useRef<Record<number, L.Layer>>({})
  const [proximityPoint, setProximityPoint] = useState<MapFeature | null>(null)
  const params = new URLSearchParams(window.location.search)
  const sharedCenter = params.has('lat') && params.has('lng')
    ? L.latLng(Number(params.get('lat')), Number(params.get('lng')))
    : undefined
  const sharedZoom = Number(params.get('z')) || 15

  const collection = (layer: LayerId): FeatureCollection => ({ type: 'FeatureCollection', features: features[layer] })
  const toggleProximity = (feature: MapFeature, button: HTMLButtonElement) => {
    setProximityPoint((current) => {
      const next = current?.properties.osm_id === feature.properties.osm_id ? null : feature
      button.textContent = next ? 'ocultar raio de 500 m' : 'mostrar raio de 500 m'
      return next
    })
  }

  const rememberLayer = (feature: MapFeature, layer: L.Layer) => {
    layerRefs.current[feature.properties.osm_id] = layer
    layer.bindTooltip(displayName(feature), { sticky: true, direction: 'top' })
    layer.bindPopup(createPopupContent(feature, (button) => toggleProximity(feature, button)))
  }

  const proximityCenter = proximityPoint ? pointLatLng(proximityPoint) : null

  useEffect(() => {
    Object.entries(layerRefs.current).forEach(([id, layer]) => {
      const popup = (layer as L.Layer & { getPopup?: () => L.Popup | undefined }).getPopup?.()
      const content = popup?.getContent()
      if (!(content instanceof HTMLElement)) return
      const button = content.querySelector<HTMLButtonElement>('.popup-proximity')
      if (button) button.textContent = Number(id) === proximityPoint?.properties.osm_id
        ? 'ocultar raio de 500 m'
        : 'mostrar raio de 500 m'
    })
  }, [proximityPoint])

  return (
    <div className="map-wrap">
      <MapContainer
        ref={mapRef}
        bounds={sharedCenter ? undefined : initialBounds}
        center={sharedCenter}
        zoom={sharedCenter ? sharedZoom : undefined}
        minZoom={12}
        maxBounds={explorationBounds}
        maxBoundsViscosity={0.65}
        zoomControl
        keyboard
        className="map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />
        <Rectangle
          bounds={studyBounds}
          pathOptions={{ color: '#284B40', weight: 1.2, opacity: 0.68, fill: false, dashArray: '5 7' }}
        >
          <Tooltip sticky>área de estudo · não é limite administrativo</Tooltip>
        </Rectangle>
        <GeoJSON
          key={`vias-${features.vias.map((feature) => feature.properties.osm_id).join('-')}`}
          data={collection('vias')}
          style={{ color: layerMeta.vias.color, weight: 1.35, opacity: 0.58 }}
          onEachFeature={(feature, layer) => rememberLayer(feature as MapFeature, layer)}
        />
        <GeoJSON
          key={`areas-${features.areas.map((feature) => feature.properties.osm_id).join('-')}`}
          data={collection('areas')}
          style={{ color: '#5d8e70', fillColor: layerMeta.areas.color, fillOpacity: 0.62, weight: 1.2 }}
          onEachFeature={(feature, layer) => rememberLayer(feature as MapFeature, layer)}
        />
        {proximityCenter && (
          <Circle
            center={proximityCenter}
            radius={PROXIMITY_RADIUS_METERS}
            pathOptions={{ color: layerMeta.pontos.color, weight: 1.5, opacity: 0.9, fillColor: layerMeta.pontos.color, fillOpacity: 0.14, dashArray: '6 5' }}
          />
        )}
        <GeoJSON
          key={`pontos-${features.pontos.map((feature) => feature.properties.osm_id).join('-')}`}
          data={collection('pontos')}
          pointToLayer={(_, latlng) => L.circleMarker(latlng, { radius: 6, color: '#f6f5f0', weight: 2, fillColor: layerMeta.pontos.color, fillOpacity: 1 })}
          onEachFeature={(feature, layer) => rememberLayer(feature as MapFeature, layer)}
        />
        <UrlState />
        <ResetView />
        <Selection id={selectedId} refs={layerRefs} />
      </MapContainer>
      <p className="map-note">recorte de estudo · região central de jacareí</p>
      {proximityPoint && (
        <aside className="proximity-note" aria-live="polite">
          <strong>raio de 500 m</strong>
          <span>distância em linha reta — não representa rota ou área oficial de atendimento</span>
          <button onClick={() => setProximityPoint(null)}>desativar</button>
        </aside>
      )}
    </div>
  )
}
