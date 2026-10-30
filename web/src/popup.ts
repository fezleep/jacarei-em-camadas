import { displayName, formatCategory, pointGroupFor, pointGroups, type MapFeature } from './data'

export function createPopupContent(feature: MapFeature, onToggleProximity: (button: HTMLButtonElement) => void) {
  const tags = feature.properties.tags_osm ?? {}
  const address = [tags['addr:street'], tags['addr:housenumber']].filter(Boolean).join(', ')
  const article = document.createElement('article')
  article.className = 'popup-content'
  const type = document.createElement('p')
  type.className = 'popup-content__type'
  type.textContent = formatCategory(feature.properties.classe_osm)
  const title = document.createElement('h3')
  title.textContent = displayName(feature)
  article.append(type, title)
  const group = pointGroupFor(feature.properties.classe_osm)
  if (group) {
    const groupLine = document.createElement('p')
    groupLine.className = 'popup-content__group'
    groupLine.textContent = `grupo: ${pointGroups[group].label}`
    article.append(groupLine)
  }
  if (address) {
    const line = document.createElement('p')
    line.textContent = address
    article.append(line)
  }
  if (tags.surface) {
    const surface = document.createElement('p')
    surface.textContent = `superfície: ${formatCategory(tags.surface)}`
    article.append(surface)
  }
  const source = document.createElement('small')
  source.textContent = `fonte: ${feature.properties.origem}`
  article.append(source)
  if (feature.geometry.type === 'Point') {
    const proximity = document.createElement('button')
    proximity.className = 'popup-proximity'
    proximity.type = 'button'
    proximity.textContent = 'mostrar raio de 500 m'
    proximity.addEventListener('click', () => onToggleProximity(proximity))
    article.append(proximity)
  }
  return article
}
