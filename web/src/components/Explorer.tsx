import { useMemo, useState } from 'react'
import type { LayerId } from '../data'
import { allFeatures, data, displayName, formatCategory, layerMeta, matchesCategory, pointGroups, searchableText } from '../data'
import { MapView } from './MapView'

export function Explorer() {
  const [visible, setVisible] = useState<Record<LayerId, boolean>>({ vias: true, areas: true, pontos: true })
  const [panelOpen, setPanelOpen] = useState(() => !window.matchMedia('(max-width: 760px)').matches)
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('todas')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [shareLabel, setShareLabel] = useState('compartilhar')

  const categoriesByLayer = useMemo(() => ({
    vias: [...new Set(data.vias.features.map((feature) => feature.properties.classe_osm))].sort((a, b) => formatCategory(a).localeCompare(formatCategory(b), 'pt-BR')),
    areas: [...new Set(data.areas.features.map((feature) => feature.properties.classe_osm))].sort((a, b) => formatCategory(a).localeCompare(formatCategory(b), 'pt-BR')),
  }), [])

  const normalized = query.trim().toLocaleLowerCase('pt-BR')
  const filtered = useMemo(() => allFeatures.filter(({ feature, layer }) => {
    if (!visible[layer]) return false
    if (!matchesCategory(feature, layer, category)) return false
    if (!normalized) return true
    return searchableText(feature, layer).includes(normalized)
  }), [category, normalized, visible])

  const filteredByLayer = useMemo(() => ({
    vias: filtered.filter((item) => item.layer === 'vias').map((item) => item.feature),
    areas: filtered.filter((item) => item.layer === 'areas').map((item) => item.feature),
    pontos: filtered.filter((item) => item.layer === 'pontos').map((item) => item.feature),
  }), [filtered])

  const share = async () => {
    const payload = { title: 'jacareí em camadas', text: 'explore jacareí, camada por camada.', url: window.location.href }
    const useNativeShare = typeof navigator.share === 'function'
    try {
      if (useNativeShare) await navigator.share(payload)
      else await navigator.clipboard.writeText(payload.url)
      setShareLabel(useNativeShare ? 'compartilhado' : 'link copiado')
      window.setTimeout(() => setShareLabel('compartilhar'), 1800)
    } catch (error) {
      if ((error as DOMException).name !== 'AbortError') setShareLabel('não foi possível')
    }
  }

  return (
    <section className="explorer" id="mapa" aria-label="explorador cartográfico">
      <aside className={`panel ${panelOpen ? '' : 'panel--closed'}`}>
        <button className="panel__toggle" onClick={() => setPanelOpen(!panelOpen)} aria-expanded={panelOpen} aria-label={`${panelOpen ? 'recolher' : 'abrir'} controles`}>
          <span aria-hidden="true">{panelOpen ? '←' : '→'}</span>
        </button>
        <div className="panel__content">
          <p className="eyebrow">explorar dados</p>
          <label className="search">
            <span className="sr-only">pesquisar por nome ou categoria</span>
            <span aria-hidden="true">⌕</span>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="buscar nome ou categoria" />
            {query && <button onClick={() => setQuery('')} aria-label="limpar pesquisa">×</button>}
          </label>

          <label className="select-label">
            categoria
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              <option value="todas">todas as categorias</option>
              <optgroup label="vias">
                {categoriesByLayer.vias.map((item) => <option key={item} value={`vias:${item}`}>{formatCategory(item)}</option>)}
              </optgroup>
              <optgroup label="áreas verdes">
                {categoriesByLayer.areas.map((item) => <option key={item} value={`areas:${item}`}>{formatCategory(item)}</option>)}
              </optgroup>
              {Object.entries(pointGroups).map(([groupId, group]) => (
                <optgroup key={groupId} label={`pontos · ${group.label}`}>
                  <option value={`pontos-grupo:${groupId}`}>todos em {group.label}</option>
                  {group.classes.map((item) => <option key={item} value={`pontos:${item}`}>{formatCategory(item)}</option>)}
                </optgroup>
              ))}
            </select>
          </label>

          <fieldset className="layers">
            <legend>camadas</legend>
            {(Object.keys(layerMeta) as LayerId[]).map((layer) => (
              <label className="layer-row" key={layer}>
                <input type="checkbox" checked={visible[layer]} onChange={() => setVisible({ ...visible, [layer]: !visible[layer] })} />
                <span className="layer-row__swatch" style={{ '--layer-color': layerMeta[layer].color } as React.CSSProperties} />
                <span>{layerMeta[layer].label}</span>
                <strong>{visible[layer] ? filteredByLayer[layer].length : data[layer].features.length}</strong>
              </label>
            ))}
          </fieldset>

          <p className="result-count" aria-live="polite">{filtered.length} {filtered.length === 1 ? 'resultado visível' : 'resultados visíveis'}</p>
          {(query || category !== 'todas') && filtered.slice(0, 6).map(({ feature, layer }) => (
            <button className="result" key={`${layer}-${feature.properties.osm_id}`} onClick={() => setSelectedId(feature.properties.osm_id)}>
              <span>{displayName(feature)}</span><small>{layerMeta[layer].label} · {formatCategory(feature.properties.classe_osm)}</small>
            </button>
          ))}
          {filtered.length === 0 && <p className="empty">nenhum lugar corresponde a esses filtros.</p>}

          <button className="share-button" onClick={share}><span aria-hidden="true">↗</span> {shareLabel}</button>
        </div>
      </aside>

      <MapView features={filteredByLayer} selectedId={selectedId} />
    </section>
  )
}
