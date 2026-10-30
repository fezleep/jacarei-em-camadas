import type { Feature, FeatureCollection, Geometry } from 'geojson'
import viasRaw from '../../dados/processados/vias.geojson?raw'
import areasRaw from '../../dados/processados/areas_verdes.geojson?raw'
import pontosRaw from '../../dados/processados/equipamentos_candidatos.geojson?raw'

export type Properties = {
  osm_id: number
  osm_type: string
  nome?: string
  classe_osm: string
  origem: string
  tags_osm?: Record<string, string>
  gestao_publica_verificada?: boolean
  observacao?: string
}

export type MapFeature = Feature<Geometry, Properties>
export type MapData = FeatureCollection<Geometry, Properties>
export type LayerId = 'vias' | 'areas' | 'pontos'

const parse = (value: string): MapData => JSON.parse(value) as MapData

export const data: Record<LayerId, MapData> = {
  vias: parse(viasRaw),
  areas: parse(areasRaw),
  pontos: parse(pontosRaw),
}

export const layerMeta = {
  vias: { label: 'vias', color: '#647B93' },
  areas: { label: 'áreas verdes', color: '#92C9A5' },
  pontos: { label: 'pontos de interesse', color: '#EB8545' },
} satisfies Record<LayerId, { label: string; color: string }>

export const allFeatures = (Object.keys(data) as LayerId[]).flatMap((layer) =>
  data[layer].features.map((feature) => ({ feature, layer })),
)

export const displayName = (feature: MapFeature) =>
  feature.properties.nome?.trim() || 'sem nome informado'

export const categoryLabels: Record<string, string> = {
  cycleway: 'ciclovia',
  footway: 'via para pedestres',
  path: 'caminho',
  primary: 'via primária',
  residential: 'via residencial',
  secondary: 'via secundária',
  service: 'via de serviço',
  tertiary: 'via terciária',
  garden: 'jardim',
  grass: 'área gramada',
  park: 'parque ou praça',
  wood: 'área arborizada',
  clinic: 'clínica',
  college: 'faculdade',
  doctors: 'consultório médico',
  government: 'órgão governamental',
  hospital: 'hospital',
  library: 'biblioteca',
  police: 'polícia',
  post_office: 'agência postal',
  school: 'escola',
  townhall: 'prefeitura',
}

export const formatCategory = (value: string) =>
  categoryLabels[value] ?? value.replaceAll('_', ' ').replaceAll('-', ' ')

export type PointGroup = 'saude' | 'educacao' | 'seguranca' | 'servicos'

export const pointGroups: Record<PointGroup, { label: string; classes: string[] }> = {
  saude: { label: 'saúde', classes: ['clinic', 'doctors', 'hospital'] },
  educacao: { label: 'educação e cultura', classes: ['college', 'library', 'school'] },
  seguranca: { label: 'segurança', classes: ['police'] },
  servicos: { label: 'serviços e administração', classes: ['government', 'post_office', 'townhall'] },
}

export const pointGroupFor = (category: string) =>
  (Object.entries(pointGroups).find(([, group]) => group.classes.includes(category))?.[0] as PointGroup | undefined)

export const searchableText = (feature: MapFeature, layer: LayerId) => {
  const group = layer === 'pontos' ? pointGroupFor(feature.properties.classe_osm) : undefined
  return [
    displayName(feature),
    feature.properties.classe_osm,
    formatCategory(feature.properties.classe_osm),
    group ? pointGroups[group].label : '',
    layerMeta[layer].label,
  ].join(' ').toLocaleLowerCase('pt-BR')
}

export const matchesCategory = (feature: MapFeature, layer: LayerId, filter: string) => {
  if (filter === 'todas') return true
  if (filter.startsWith('pontos-grupo:')) {
    const groupId = filter.split(':')[1] as PointGroup
    return layer === 'pontos' && Boolean(pointGroups[groupId]?.classes.includes(feature.properties.classe_osm))
  }
  return `${layer}:${feature.properties.classe_osm}` === filter
}
