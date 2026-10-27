"""Gera uma cópia portátil do QGZ final para distribuição no GitHub."""
from pathlib import Path

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsProject,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "qgis" / "jacarei_em_camadas_centro_portfolio_v2.qgz"
OUTPUT = ROOT / "qgis" / "jacarei_em_camadas_centro_portfolio_publicacao.qgz"
NORTH = ROOT / "qgis" / "simbolos" / "seta_norte.svg"

if OUTPUT.exists():
    raise FileExistsError(f"Saída já existe: {OUTPUT}")
if not SOURCE.is_file() or not NORTH.is_file():
    raise FileNotFoundError("Projeto v2 ou símbolo norte não encontrado")

app = QgsApplication([], True)
app.initQgis()
try:
    project = QgsProject.instance()
    if not project.read(str(SOURCE)):
        raise RuntimeError(f"Falha ao abrir {SOURCE}")
    if project.crs().authid() != "EPSG:31983" or len(project.mapLayers()) != 3:
        raise RuntimeError("CRS ou número de camadas inesperado")

    layout = project.layoutManager().layoutByName("Mapa 01 - Regiao Central")
    north = next(
        item for item in layout.items()
        if isinstance(item, QgsLayoutItemPicture) and item.id() == "seta_norte"
    )
    north.setPicturePath(str(NORTH))
    map_item = next(item for item in layout.items() if isinstance(item, QgsLayoutItemMap))
    # O mapa passa a acompanhar as três camadas do projeto. Isso evita que o
    # XML do layout memorize cópias absolutas dos caminhos de origem.
    map_item.setKeepLayerSet(False)
    map_item.setLayers([])
    project.gpsSettings().setDestinationLayer(None)
    project.setFilePathStorage(Qgis.FilePathType.Relative)
    project.setFileName(str(OUTPUT))
    if not project.write():
        raise OSError(f"Falha ao salvar {OUTPUT}")
    print(f"Projeto portátil salvo: {OUTPUT}")
finally:
    QgsProject.instance().clear()
    app.exitQgis()
