"""Executar pelo editor do Console Python do QGIS Desktop (NÃO pelo Python comum).

Requer que scripts/baixar_osm.py e validar_geojson.py tenham sido executados.
No Console Python: clicar em Mostrar editor, abrir este arquivo, Executar.
"""
from pathlib import Path

from qgis.core import (
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsFillSymbol,
    QgsLineSymbol, QgsMarkerSymbol, QgsProject, QgsRectangle,
    QgsSingleSymbolRenderer, QgsVectorLayer,
)

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'dados' / 'processados'
files = [
    ('vias.geojson', 'Vias — OpenStreetMap', 'line'),
    ('areas_verdes.geojson', 'Áreas verdes — OpenStreetMap', 'fill'),
    ('equipamentos_candidatos.geojson', 'Equipamentos candidatos — conferir gestão', 'point'),
]
project = QgsProject.instance()
output = ROOT / 'qgis' / 'jacarei_em_camadas_centro.qgz'
if output.exists():
    raise FileExistsError(f'Projeto já existe; nenhuma alteração realizada: {output}')
if project.fileName() or project.isDirty() or project.mapLayers():
    raise RuntimeError('Abra um projeto QGIS NOVO e VAZIO antes de executar. Nada foi modificado.')
# Pré-validação das três camadas antes de alterar a sessão do QGIS.
added = []
for name, title, kind in files:
    filename = INPUT / name
    if not filename.is_file():
        raise FileNotFoundError(f'Camada ausente: {filename}. Execute o coletor.')
    layer = QgsVectorLayer(str(filename), title, 'ogr')
    if not layer.isValid() or layer.featureCount() == 0:
        raise ValueError(f'Camada inválida ou vazia: {filename}')
    if kind == 'line':
        symbol = QgsLineSymbol.createSimple({'line_color': '94,112,135,255', 'line_width': '0.35'})
    elif kind == 'fill':
        symbol = QgsFillSymbol.createSimple({'color': '96,175,115,180', 'outline_color': '45,122,75,255', 'outline_width': '0.18'})
    else:
        symbol = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': '235,116,55,255', 'outline_color': '255,255,255,255', 'size': '2.3'})
    layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    added.append(layer)

project.setCrs(QgsCoordinateReferenceSystem('EPSG:31983'))
for layer in added:
    project.addMapLayer(layer)

# Extensão fixa do recorte piloto, transformada em metros no CRS do projeto.
w, s, e, n = (-45.9750, -23.3060, -45.9600, -23.2960)
transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), project.crs(), project)
view = transform.transformBoundingBox(QgsRectangle(w, s, e, n))
view.scale(1.08)
iface.mapCanvas().setExtent(view)
iface.mapCanvas().refresh()
project.setFileName(str(output))
if not project.write():
    raise OSError(f'Não foi possível salvar: {output}')
print(f'QGIS salvo: {output}')
print('Abra o Layout ou use Projeto > Importar/Exportar > Exportar mapa para imagem para o PNG.')
