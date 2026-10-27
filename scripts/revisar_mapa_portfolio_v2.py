"""Cria a revisão v2 do mapa de portfólio sem alterar a versão aprovada."""
from __future__ import annotations

import sys
from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsProject,
    QgsUnitTypes,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qgis" / "jacarei_em_camadas_centro_portfolio.qgz"
OUTPUT = ROOT / "qgis" / "jacarei_em_camadas_centro_portfolio_v2.qgz"
PNG = ROOT / "mapas" / "jacarei_em_camadas_centro_portfolio_v2_300dpi.png"
PDF = ROOT / "mapas" / "jacarei_em_camadas_centro_portfolio_v2.pdf"
MM = QgsUnitTypes.LayoutMillimeters


def move_resize(item, x: float, y: float, width: float, height: float) -> None:
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    item.attemptResize(QgsLayoutSize(width, height, MM))


def add_label(layout, item_id: str, text: str, x: float, y: float,
              width: float, height: float, size: float, bold: bool = False,
              color: str = "#263746", centered: bool = False) -> QgsLayoutItemLabel:
    label = QgsLayoutItemLabel(layout)
    label.setId(item_id)
    label.setText(text)
    font = QFont("Arial")
    font.setPointSizeF(size)
    font.setBold(bold)
    label.setFont(font)
    label.setFontColor(QColor(color))
    label.setMarginX(0)
    label.setMarginY(0)
    label.setVAlign(Qt.AlignTop)
    if centered:
        label.setHAlign(Qt.AlignHCenter)
    move_resize(label, x, y, width, height)
    layout.addLayoutItem(label)
    return label


def main() -> int:
    for path in (SOURCE,):
        if not path.is_file():
            raise FileNotFoundError(path)
    existing = [path for path in (OUTPUT, PNG, PDF) if path.exists()]
    if existing:
        raise FileExistsError(
            "Saídas v2 já existem; revise antes de removê-las: "
            + ", ".join(map(str, existing))
        )

    app = QgsApplication([], True)
    app.initQgis()
    try:
        project = QgsProject.instance()
        if not project.read(str(SOURCE)):
            raise RuntimeError(f"Falha ao abrir {SOURCE}")
        if project.crs().authid() != "EPSG:31983":
            raise RuntimeError(f"CRS inesperado: {project.crs().authid()}")
        counts = sorted(layer.featureCount() for layer in project.mapLayers().values())
        if counts != [14, 25, 334] or len(project.mapLayers()) != 3:
            raise RuntimeError(f"Camadas ou contagens inesperadas: {counts}")

        layout = project.layoutManager().layoutByName("Mapa 01 - Regiao Central")
        if layout is None:
            raise RuntimeError("Layout aprovado não encontrado")
        maps = [item for item in layout.items() if isinstance(item, QgsLayoutItemMap)]
        if len(maps) != 1 or maps[0].mapRotation() != 0:
            raise RuntimeError("Mapa ausente, duplicado ou rotacionado")
        map_item = maps[0]

        # 1. Troca somente o pictograma, mantendo vínculo e norte no topo.
        north_items = [
            item for item in layout.items()
            if isinstance(item, QgsLayoutItemPicture) and item.id() == "seta_norte"
        ]
        if len(north_items) != 1:
            raise RuntimeError("Seta norte aprovada não encontrada")
        north = north_items[0]
        north.setPicturePath(
            str(Path(QgsApplication.prefixPath()) / "svg" / "arrows" / "NorthArrow_04.svg")
        )
        north.setResizeMode(QgsLayoutItemPicture.Zoom)
        north.setLinkedMap(map_item)
        north.setPictureRotation(map_item.mapRotation())
        move_resize(north, 210.5, 188.5, 11, 13.5)
        add_label(
            layout, "seta_norte_letra", "N",
            209.5, 183.8, 13, 5, 9.5, True, "#111111", True,
        )

        # 2. Separa título e corpo para dar respiro, sem mudar a largura do painel.
        old_info = layout.itemById("informacoes")
        if old_info is None:
            raise RuntimeError("Bloco técnico aprovado não encontrado")
        layout.removeLayoutItem(old_info)
        add_label(
            layout, "informacoes_titulo", "INFORMAÇÕES TÉCNICAS",
            232, 94, 59, 5, 8.0, True,
        )
        add_label(
            layout, "informacoes_corpo",
            "Fonte: © OpenStreetMap contributors\n"
            "Licença: ODbL\n\n"
            "Coleta: 22 out. 2026 (UTC)\n"
            "Base OSM: 22 out. 2026, 13:32 UTC\n\n"
            "Projeto: SIRGAS 2000 / UTM 23S\n"
            "EPSG:31983\n\n"
            "Recorte de estudo — não corresponde a\n"
            "limite administrativo oficial.",
            232, 100, 59, 52, 7.2,
        )

        layout.refresh()
        project.setFileName(str(OUTPUT))
        if not project.write():
            raise OSError(f"Não foi possível salvar {OUTPUT}")

        exporter = QgsLayoutExporter(layout)
        image_settings = QgsLayoutExporter.ImageExportSettings()
        image_settings.dpi = 300
        if exporter.exportToImage(str(PNG), image_settings) != QgsLayoutExporter.Success:
            raise RuntimeError("Falha na exportação PNG")

        # 3. Mantém vetores e solicita texto real, selecionável, em vez de contornos.
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.dpi = 300
        pdf_settings.forceVectorOutput = True
        pdf_settings.rasterizeWholeImage = False
        pdf_settings.textRenderFormat = Qgis.TextRenderFormat.AlwaysText
        pdf_settings.exportMetadata = True
        if exporter.exportToPdf(str(PDF), pdf_settings) != QgsLayoutExporter.Success:
            raise RuntimeError("Falha na exportação PDF")

        print(f"PROJETO={OUTPUT}")
        print(f"PNG={PNG}")
        print(f"PDF={PDF}")
        print("PDF_TEXT_MODE=AlwaysText; forceVectorOutput=True; rasterizeWholeImage=False")
        return 0
    finally:
        QgsProject.instance().clear()
        app.exitQgis()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise
