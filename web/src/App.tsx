import { useEffect, useState } from 'react'
import { About } from './components/About'
import { Explorer } from './components/Explorer'
import { Intro } from './components/Intro'

type Theme = 'light' | 'dark'

const getInitialTheme = (): Theme => {
  const saved = localStorage.getItem('jacarei-theme')
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default function App() {
  const [exploring, setExploring] = useState(() => window.location.hash === '#mapa')
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const [aboutOpen, setAboutOpen] = useState(false)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('jacarei-theme', theme)
  }, [theme])

  const startExploring = () => {
    window.location.hash = 'mapa'
    setExploring(true)
  }

  return (
    <main className={exploring ? 'app app--exploring' : 'app'}>
      <header className="topbar">
        <div className="brand">
          <button className="wordmark" onClick={() => setExploring(false)} aria-label="voltar ao início">
            jacareí <span>em camadas</span>
          </button>
          <a className="signature" href="https://github.com/fezleep" target="_blank" rel="noreferrer">feito por <strong>Felipe Virginio</strong></a>
        </div>
        <nav aria-label="atalhos">
          <button className="quiet-button" onClick={() => setAboutOpen(true)}>sobre</button>
          <button
            className="icon-button"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            aria-label={`usar modo ${theme === 'light' ? 'escuro' : 'claro'}`}
            title={`modo ${theme === 'light' ? 'escuro' : 'claro'}`}
          >
            {theme === 'light' ? '◐' : '○'}
          </button>
        </nav>
      </header>

      {exploring ? <Explorer /> : <Intro onExplore={startExploring} />}
      <About open={aboutOpen} onClose={() => setAboutOpen(false)} />
    </main>
  )
}
