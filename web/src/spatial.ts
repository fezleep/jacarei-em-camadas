import type { Geometry } from 'geojson'
import type { MapFeature } from './data'

export const PROXIMITY_RADIUS_METERS = 500

export const pointLatLng = (feature: MapFeature): [number, number] | null => {
  if (feature.geometry.type !== 'Point') return null
  const [longitude, latitude] = feature.geometry.coordinates
  return [latitude, longitude]
}

export const extentOf = (features: MapFeature[]): [[number, number], [number, number]] => {
  let west = Infinity
  let south = Infinity
  let east = -Infinity
  let north = -Infinity

  const visit = (coordinates: unknown): void => {
    if (!Array.isArray(coordinates)) return
    if (typeof coordinates[0] === 'number' && typeof coordinates[1] === 'number') {
      const [longitude, latitude] = coordinates as [number, number]
      west = Math.min(west, longitude)
      east = Math.max(east, longitude)
      south = Math.min(south, latitude)
      north = Math.max(north, latitude)
      return
    }
    coordinates.forEach(visit)
  }

  features.forEach((feature) => visit((feature.geometry as Geometry & { coordinates?: unknown }).coordinates))
  if (![west, south, east, north].every(Number.isFinite)) throw new Error('não foi possível calcular a extensão dos dados')
  return [[south, west], [north, east]]
}
