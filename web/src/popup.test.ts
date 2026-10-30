// @vitest-environment jsdom
import { describe, expect, it, vi } from 'vitest'
import { data } from './data'
import { createPopupContent } from './popup'

describe('popups cartográficos', () => {
  it('exibe conteúdo traduzido sem interpretar HTML externo', () => {
    const feature = structuredClone(data.pontos.features.find((item) => item.properties.classe_osm === 'hospital')!)
    feature.properties.nome = '<img src=x onerror=alert(1)>'
    const popup = createPopupContent(feature, vi.fn())
    expect(popup.querySelector('h3')?.textContent).toBe('<img src=x onerror=alert(1)>')
    expect(popup.querySelector('img')).toBeNull()
    expect(popup.textContent).toContain('grupo: saúde')
  })

  it('oferece a proximidade apenas em pontos e aciona o controle', () => {
    const callback = vi.fn()
    const pointPopup = createPopupContent(data.pontos.features[0], callback)
    const button = pointPopup.querySelector<HTMLButtonElement>('.popup-proximity')!
    button.click()
    expect(callback).toHaveBeenCalledWith(button)
    expect(button.textContent).toBe('mostrar raio de 500 m')

    const roadPopup = createPopupContent(data.vias.features[0], callback)
    expect(roadPopup.querySelector('.popup-proximity')).toBeNull()
  })
})
