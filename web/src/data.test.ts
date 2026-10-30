import { describe, expect, it } from 'vitest'
import { data, displayName, formatCategory, matchesCategory, pointGroupFor, searchableText } from './data'
import { extentOf, pointLatLng, PROXIMITY_RADIUS_METERS } from './spatial'

describe('dados cartográficos', () => {
  it('carrega as três fontes com as contagens publicadas', () => {
    expect(data.vias.features).toHaveLength(334)
    expect(data.areas.features).toHaveLength(14)
    expect(data.pontos.features).toHaveLength(25)
  })

  it('preserva os tipos de geometria esperados', () => {
    expect(data.vias.features.every((item) => ['LineString', 'MultiLineString'].includes(item.geometry.type))).toBe(true)
    expect(data.areas.features.every((item) => ['Polygon', 'MultiPolygon'].includes(item.geometry.type))).toBe(true)
    expect(data.pontos.features.every((item) => item.geometry.type === 'Point')).toBe(true)
  })

  it('oferece nome seguro quando o dado não tem nome', () => {
    const unnamed = data.vias.features.find((item) => !item.properties.nome)
    expect(unnamed).toBeDefined()
    expect(displayName(unnamed!)).toBe('sem nome informado')
  })

  it('traduz categorias sem alterar os valores OSM', () => {
    expect(formatCategory('post_office')).toBe('agência postal')
    expect(pointGroupFor('hospital')).toBe('saude')
    expect(pointGroupFor('police')).toBe('seguranca')
    expect(data.pontos.features.some((item) => item.properties.classe_osm === 'post_office')).toBe(true)
  })

  it('inclui nomes traduzidos e grupos na pesquisa', () => {
    const hospital = data.pontos.features.find((item) => item.properties.classe_osm === 'hospital')!
    expect(searchableText(hospital, 'pontos')).toContain('saúde')
    expect(searchableText(hospital, 'pontos')).toContain('hospital')
    expect(matchesCategory(hospital, 'pontos', 'pontos-grupo:saude')).toBe(true)
    expect(matchesCategory(hospital, 'pontos', 'pontos-grupo:educacao')).toBe(false)
  })

  it('deriva a extensão conjunta e configura a proximidade em metros', () => {
    const features = [...data.vias.features, ...data.areas.features, ...data.pontos.features]
    const [[south, west], [north, east]] = extentOf(features)
    expect(south).toBeLessThan(north)
    expect(west).toBeLessThan(east)
    expect(PROXIMITY_RADIUS_METERS).toBe(500)
    const point = data.pontos.features[0]
    const coordinates = point.geometry.type === 'Point' ? point.geometry.coordinates : []
    expect(pointLatLng(point)).toEqual([coordinates[1], coordinates[0]])
  })
})
