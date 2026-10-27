"""Valida sintaxe, tipo, geometria, coordenadas e recorte dos GeoJSON OSM."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from shapely.geometry import box, shape

ROOT = Path(__file__).resolve().parents[1]
BBOX = (-45.9750, -23.3060, -45.9600, -23.2960)
EXPECTED = {
    'vias.geojson': {'LineString', 'MultiLineString'},
    'areas_verdes.geojson': {'Polygon', 'MultiPolygon'},
    'equipamentos_candidatos.geojson': {'Point'},
}


def validate_file(path: Path, allowed_types: set[str], bbox=BBOX):
    errors = []
    if not path.is_file():
        return 0, [f'Arquivo não encontrado: {path}']
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        return 0, [f'JSON inválido: {exc}']
    if data.get('type') != 'FeatureCollection' or not isinstance(data.get('features'), list):
        return 0, ['Esperado FeatureCollection com features em lista']
    clip = box(*bbox)
    for idx, feature in enumerate(data['features']):
        try:
            if feature.get('type') != 'Feature':
                raise ValueError('type não é Feature')
            geom = shape(feature['geometry'])
            if geom.is_empty or not geom.is_valid:
                raise ValueError('geometria vazia ou inválida')
            if geom.geom_type not in allowed_types:
                raise ValueError(f'tipo inesperado: {geom.geom_type}')
            if not geom.intersects(clip):
                raise ValueError('fora do recorte')
            minx, miny, maxx, maxy = geom.bounds
            if not (-180 <= minx <= 180 and -180 <= maxx <= 180
                    and -90 <= miny <= 90 and -90 <= maxy <= 90):
                raise ValueError('coordenadas não parecem EPSG:4326')
            if 'osm_id' not in feature.get('properties', {}):
                raise ValueError('osm_id ausente')
        except (TypeError, KeyError, ValueError) as exc:
            errors.append(f'feature #{idx}: {exc}')
    return len(data['features']), errors


def main():
    failed = False
    print('Validando GeoJSON (WGS84 / longitude, latitude):')
    for name, allowed in EXPECTED.items():
        path = ROOT / 'dados' / 'processados' / name
        count, errors = validate_file(path, allowed)
        print(f'  {name}: {count} elementos | {len(errors)} erro(s)')
        for e in errors[:8]:
            print('    - ' + e)
        if errors or count == 0:
            failed = True
            if not errors:
                print('    - camada vazia: verificar cobertura e filtros OSM')
    if failed:
        print('FALHA: as três camadas ainda não estão validadas.')
        sys.exit(1)
    print('OK: três GeoJSON geograficamente válidos dentro do recorte.')


if __name__ == '__main__':
    main()
