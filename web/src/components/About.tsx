import { useEffect, useRef } from 'react'

type Props = { open: boolean; onClose: () => void }

export function About({ open, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog className="about" ref={dialogRef} onClose={onClose} onClick={(event) => {
      if (event.target === dialogRef.current) onClose()
    }}>
      <button className="about__close" onClick={onClose} aria-label="fechar">×</button>
      <p className="eyebrow">sobre</p>
      <h2>um mapa para explorar jacareí com calma.</h2>
      <p>
        este projeto independente aproxima desenvolvimento de software e geoprocessamento. o recorte é uma área de estudo da região central, não um limite administrativo oficial.
      </p>
      <p>
        os dados vêm do OpenStreetMap e podem conter omissões ou classificações desatualizadas. os pontos de interesse foram selecionados por tags OSM; a gestão pública não foi verificada individualmente.
      </p>
      <div className="about__links">
        <a href="https://github.com/fezleep/jacarei-em-camadas" target="_blank" rel="noreferrer">código e documentação ↗</a>
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">dados © openstreetmap contributors · odbl ↗</a>
      </div>
      <p className="about__author">feito por <a href="https://github.com/fezleep" target="_blank" rel="noreferrer">felipe virginio</a>.</p>
    </dialog>
  )
}
