"""Finaliza e exporta o mapa de portfólio a partir do projeto QGIS existente.

Executar com o ambiente Python do QGIS (veja documentacao/reproducao_missao02.md).
O projeto original nunca é sobrescrito.
"""
from __future__ import annotations

import sys
from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFillSymbol,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsProject,
    QgsRectangle,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qgis" / "jacarei_em_camadas_centro.qgz"
OUTPUT = ROOT / "qgis" / "jacarei_em_camadas_centro_portfolio.qgz"
PNG = ROOT / "mapas" / "jacarei_em_camadas_centro_portfolio_300dpi.png"
PDF = ROOT / "mapas" / "jacarei_em_camadas_centro_portfolio.pdf"
LAYOUT_NAME = "Mapa 01 - Regiao Central"
MM = QgsUnitTypes.LayoutMillimeters


def move_resize(item, x: float, y: float, width: float, height: float) -> None:
    item.attemptMove(QgsLayoutPoint(x, y, MM))
    item.attemptResize(QgsLayoutSize(width, height, MM))


def add_label(layout, item_id: str, text: str, x: float, y: float,
              width: float, height: float, size: float, bold: bool = False,
              color: str = "#263746") -> QgsLayoutItemLabel:
    item = QgsLayoutItemLabel(layout)
    item.setId(item_id)
    item.setText(text)
    font = QFont("Arial")
    font.setPointSizeF(size)
    font.setBold(bold)
    item.setFont(font)
    item.setFontColor(QColor(color))
    item.setMarginX(0)
    item.setMarginY(0)
    item.setVAlign(Qt.AlignTop)
    move_resize(item, x, y, width, height)
    layout.addLayoutItem(item)
    return item


def layer_by_fragment(project: QgsProject, fragment: str):
    for layer in project.mapLayers().values():
        if fragment.casefold() in layer.name().casefold():
            return layer
    raise RuntimeError(f"Camada não encontrada: {fragment}")


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    if OUTPUT.exists():
        raise FileExistsError(
            f"A saída já existe; remova-a manualmente após revisar: {OUTPUT}"
        )

    # GUI habilitada é necessária no Windows para carregar as fontes do sistema,
    # mesmo que nenhum diálogo seja aberto durante a exportação automatizada.
    app = QgsApplication([], True)
    app.initQgis()
    try:
        project = QgsProject.instance()
        if not project.read(str(SOURCE)):
            raise RuntimeError(f"Falha ao abrir o projeto: {SOURCE}")
        if project.crs().authid() != "EPSG:31983":
            raise RuntimeError(f"CRS inesperado: {project.crs().authid()}")

        vias = layer_by_fragment(project, "Vias")
        verdes = layer_by_fragment(project, "Áreas verdes")
        equipamentos = layer_by_fragment(project, "Equipamentos candidatos")
        expected = {vias.id(): 334, verdes.id(): 14, equipamentos.id(): 25}
        for layer in (vias, verdes, equipamentos):
            if not layer.isValid() or layer.featureCount() != expected[layer.id()]:
                raise RuntimeError(
                    f"Camada inválida ou contagem alterada: {layer.name()} "
                    f"({layer.featureCount()})"
                )
            if layer.crs().authid() != "EPSG:4326":
                raise RuntimeError(f"CRS da camada inesperado: {layer.name()}")

        vias.setName("Vias")
        verdes.setName("Áreas verdes")
        equipamentos.setName("Equipamentos candidatos")
        vias.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({
            "line_color": "100,123,147,255", "line_width": "0.25",
            "line_width_unit": "MM",
        })))
        verdes.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({
            "color": "146,201,165,205", "outline_color": "72,126,91,255",
            "outline_width": "0.18", "outline_width_unit": "MM",
        })))
        equipamentos.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({
            "name": "circle", "color": "235,133,69,255",
            "outline_color": "255,255,255,255", "outline_width": "0.25",
            "outline_width_unit": "MM", "size": "2.4", "size_unit": "MM",
        })))

        layout = project.layoutManager().layoutByName(LAYOUT_NAME)
        if layout is None:
            raise RuntimeError(f"Layout não encontrado: {LAYOUT_NAME}")
        page = layout.pageCollection().page(0)
        page.setPageSize(QgsLayoutSize(297, 210, MM))

        maps = [i for i in layout.items() if isinstance(i, QgsLayoutItemMap)]
        if len(maps) != 1:
            raise RuntimeError(f"Esperado um mapa no layout; encontrados: {len(maps)}")
        map_item = maps[0]
        map_item.setId("mapa_principal")
        move_resize(map_item, 10, 27, 215, 158)
        map_item.setFrameEnabled(True)
        map_item.setFrameStrokeColor(QColor("#B5C0C9"))
        map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.25, MM))

        transform = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:4326"), project.crs(), project
        )
        extent = transform.transformBoundingBox(
            QgsRectangle(-45.9750, -23.3060, -45.9600, -23.2960)
        )
        extent.scale(1.04)
        map_item.setExtent(extent)
        map_item.setLayers([equipamentos, vias, verdes])
        map_item.setKeepLayerSet(True)

        for item in list(layout.items()):
            if isinstance(item, (QgsLayoutItemLabel, QgsLayoutItemLegend,
                                 QgsLayoutItemPicture)):
                layout.removeLayoutItem(item)

        add_label(layout, "titulo", "JACAREÍ EM CAMADAS", 10, 8, 215, 8, 21, True)
        add_label(
            layout, "subtitulo",
            "Região central de Jacareí/SP — leitura cartográfica do OpenStreetMap",
            10, 18, 215, 6, 9.5, False, "#526777",
        )
        add_label(layout, "painel_titulo", "REGIÃO CENTRAL", 232, 10, 59, 7, 14, True)
        add_label(
            layout, "painel_subtitulo", "Vias, áreas verdes e\nequipamentos candidatos",
            232, 19, 59, 13, 9, False, "#526777",
        )

        legend = QgsLayoutItemLegend(layout)
        legend.setId("legenda_simbolica")
        legend.setTitle("LEGENDA")
        legend.setLinkedMap(map_item)
        legend.setAutoUpdateModel(False)
        root = legend.model().rootGroup()
        root.removeAllChildren()
        for layer in (vias, verdes, equipamentos):
            root.addLayer(layer)
        legend.setResizeToContents(False)
        title_style = legend.style(QgsLegendStyle.Title)
        title_font = QFont("Arial", 10)
        title_font.setBold(True)
        title_style.setFont(title_font)
        group_font = QFont("Arial")
        group_font.setPointSizeF(7.5)
        legend.style(QgsLegendStyle.SymbolLabel).setFont(group_font)
        legend.setSymbolWidth(7)
        legend.setSymbolHeight(4)
        move_resize(legend, 232, 38, 59, 50)
        layout.addLayoutItem(legend)

        add_label(
            layout, "informacoes",
            "INFORMAÇÕES TÉCNICAS\n"
            "Fonte: © OpenStreetMap contributors\n"
            "Licença: ODbL\n"
            "Coleta: 22 out. 2026 (UTC)\n"
            "Base OSM: 22 out. 2026, 13:32 UTC\n"
            "Projeto: SIRGAS 2000 / UTM 23S\n"
            "EPSG:31983\n\n"
            "Recorte de estudo — não corresponde a\n"
            "limite administrativo oficial.",
            232, 94, 59, 55, 7.4,
        )
        add_label(
            layout, "autoria",
            "AUTORIA\nFelipe Virginio\nProjeto independente, sem vínculo institucional",
            232, 157, 59, 25, 7.7,
        )
        add_label(
            layout, "nota_equipamentos",
            "Os pontos representam candidatos identificados por tags OSM;\n"
            "a gestão pública não foi verificada.",
            10, 202, 215, 6, 6.8, False, "#526777",
        )

        scale_bars = [i for i in layout.items() if isinstance(i, QgsLayoutItemScaleBar)]
        if len(scale_bars) != 1:
            raise RuntimeError(
                f"Esperada uma barra de escala; encontradas: {len(scale_bars)}"
            )
        scale = scale_bars[0]
        scale.setId("barra_escala")
        scale.setLinkedMap(map_item)
        scale.setStyle("Single Box")
        scale.setUnits(QgsUnitTypes.DistanceMeters)
        scale.setUnitsPerSegment(250)
        scale.setNumberOfSegments(4)
        scale.setNumberOfSegmentsLeft(0)
        scale.setUnitLabel("m")
        scale.setFont(QFont("Arial", 7))
        move_resize(scale, 15, 189, 55, 9)

        north = QgsLayoutItemPicture(layout)
        north.setId("seta_norte")
        north.setPicturePath(
            str(Path(QgsApplication.prefixPath()) / "svg" / "arrows" / "NorthArrow_01.svg")
        )
        north.setResizeMode(QgsLayoutItemPicture.Zoom)
        north.setLinkedMap(map_item)
        move_resize(north, 210, 188, 12, 12)
        layout.addLayoutItem(north)

        layout.refresh()
        project.setFileName(str(OUTPUT))
        if not project.write():
            raise OSError(f"Não foi possível salvar: {OUTPUT}")

        PNG.parent.mkdir(parents=True, exist_ok=True)
        exporter = QgsLayoutExporter(layout)
        image_settings = QgsLayoutExporter.ImageExportSettings()
        image_settings.dpi = 300
        image_settings.generateWorldFile = False
        png_result = exporter.exportToImage(str(PNG), image_settings)
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.dpi = 300
        pdf_result = exporter.exportToPdf(str(PDF), pdf_settings)
        if png_result != QgsLayoutExporter.Success:
            raise RuntimeError(f"Falha ao exportar PNG: código {png_result}")
        if pdf_result != QgsLayoutExporter.Success:
            raise RuntimeError(f"Falha ao exportar PDF: código {pdf_result}")

        print(f"PROJETO={OUTPUT}")
        print(f"PNG={PNG}")
        print(f"PDF={PDF}")
        print("CAMADAS=vias:334;areas_verdes:14;equipamentos_candidatos:25")
        print(f"ESCALA_APROXIMADA=1:{map_item.scale():.0f}")
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
