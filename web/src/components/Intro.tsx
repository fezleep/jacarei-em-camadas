type Props = { onExplore: () => void }

export function Intro({ onExplore }: Props) {
  return (
    <section className="intro" aria-labelledby="intro-title">
      <div className="intro__copy">
        <p className="eyebrow">uma leitura da região central</p>
        <h1 id="intro-title">jacareí,<br /><em>camada por camada.</em></h1>
        <p className="intro__description">
          vias, áreas verdes e pontos de interesse reunidos em uma experiência cartográfica aberta à descoberta.
        </p>
        <button className="primary-button" onClick={onExplore}>explorar mapa <span aria-hidden="true">→</span></button>
      </div>
      <div className="intro__art" aria-hidden="true">
        <span className="contour contour--one" />
        <span className="contour contour--two" />
        <span className="contour contour--three" />
        <span className="map-dot" />
        <p>23°18′ s<br />45°58′ o</p>
      </div>
      <p className="intro__credit">dados abertos · openstreetmap</p>
    </section>
  )
}
