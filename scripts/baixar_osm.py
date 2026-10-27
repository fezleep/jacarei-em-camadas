"""Baixa dados OSM REAIS para um recorte de estudo no Centro de Jacareí.

Uso: python scripts/baixar_osm.py
Nunca cria geometrias de exemplo em arquivos de produção.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from shapely.geometry import LineString, Point, Polygon, box, mapping
from shapely.ops import polygonize, unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dados' / 'processados'
RAW = ROOT / 'dados' / 'brutos'
# Oeste, sul, leste, norte. Recorte ANALÍTICO (não é limite oficial de bairro).
BBOX = (-45.9750, -23.3060, -45.9600, -23.2960)
API_URLS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.private.coffee/api/interpreter',
]
AMENITIES = {
    'school', 'kindergarten', 'college', 'university', 'hospital',
    'clinic', 'doctors', 'library', 'townhall', 'police', 'fire_station',
    'community_centre', 'social_facility', 'courthouse', 'post_office',
}


def overpass_query(bbox=BBOX):
    w, s, e, n = bbox
    b = f'({s},{w},{n},{e})'
    # Apenas geometrias e atributos publicados pelo OpenStreetMap.
    queries = [
        f'way["highway"~"^(residential|tertiary|secondary|primary|unclassified|service|living_street|pedestrian|footway|cycleway|path|steps)$"]{b};',
        f'way["leisure"~"^(park|garden|recreation_ground|nature_reserve)$"]{b};',
        f'way["landuse"~"^(grass|forest|recreation_ground)$"]{b};',
        f'way["natural"~"^(wood|grassland)$"]{b};',
        f'relation["leisure"~"^(park|garden|recreation_ground|nature_reserve)$"]{b};',
        f'relation["landuse"~"^(grass|forest|recreation_ground)$"]{b};',
        f'relation["natural"~"^(wood|grassland)$"]{b};',
        f'node["amenity"~"^(school|kindergarten|college|university|hospital|clinic|doctors|library|townhall|police|fire_station|community_centre|social_facility|courthouse|post_office)$"]{b};',
        f'way["amenity"~"^(school|kindergarten|college|university|hospital|clinic|doctors|library|townhall|police|fire_station|community_centre|social_facility|courthouse|post_office)$"]{b};',
        f'node["office"="government"]{b};',
        f'way["office"="government"]{b};',
    ]
    return '[out:json][timeout:60];(' + ''.join(queries) + ');out center geom;'


def download(query):
    failures = []
    for url in API_URLS:
        try:
            response = requests.post(
                url,
                data={'data': query},
                headers={'User-Agent': 'Jacarei-em-Camadas-FelipeVirginio/0.1 (OSM attribution in README)'},
                timeout=(15, 90),
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data.get('elements'), list):
                raise ValueError('Resposta não contém lista de elementos OSM')
            return data, url
        except (requests.RequestException, ValueError) as exc:
            failures.append(f'{url}: {type(exc).__name__}: {exc}')
    raise RuntimeError('Não foi possível consultar o Overpass. Nenhum arquivo foi inventado.\n' + '\n'.join(failures))


def coord_list(points):
    return [(float(p['lon']), float(p['lat'])) for p in points if 'lon' in p and 'lat' in p]


def element_geometry(item):
    typ = item.get('type')
    if typ == 'node' and 'lon' in item and 'lat' in item:
        return Point(item['lon'], item['lat'])
    if typ == 'way':
        coords = coord_list(item.get('geometry', []))
        if len(coords) < 2:
            return None
        if len(coords) >= 4 and coords[0] == coords[-1]:
            geom = Polygon(coords)
            return geom if geom.is_valid else geom.buffer(0)
        return LineString(coords)
    if typ == 'relation':
        # Multipolígonos: une linhas exteriores antes de construir polígonos.
        outer_lines, inner_lines = [], []
        for member in item.get('members', []):
            coords = coord_list(member.get('geometry', []))
            if len(coords) < 2:
                continue
            line = LineString(coords)
            if member.get('role') == 'outer':
                outer_lines.append(line)
            elif member.get('role') == 'inner':
                inner_lines.append(line)
        if not outer_lines:
            return None
        outer = list(polygonize(unary_union(outer_lines)))
        if not outer:
            return None
        g = unary_union(outer)
        inner = list(polygonize(unary_union(inner_lines))) if inner_lines else []
        if inner:
            g = g.difference(unary_union(inner))
        return g if g.is_valid else g.buffer(0)
    return None


def is_green(tags):
    return (tags.get('leisure') in {'park', 'garden', 'recreation_ground', 'nature_reserve'}
            or tags.get('landuse') in {'grass', 'forest', 'recreation_ground'}
            or tags.get('natural') in {'wood', 'grassland'})


def is_equipment(tags):
    return tags.get('amenity') in AMENITIES or tags.get('office') == 'government'


def extract_features(data, bbox=BBOX):
    clipping = box(*bbox)
    result = {'vias': [], 'areas_verdes': [], 'equipamentos_candidatos': []}
    seen = {k: set() for k in result}
    skipped = {'geometry_unavailable': 0, 'geometry_invalid_or_empty': 0}
    for el in data.get('elements', []):
        tags = el.get('tags', {})
        geom = element_geometry(el)
        if geom is None:
            skipped['geometry_unavailable'] += 1
            continue
        if geom.is_empty or not geom.is_valid:
            skipped['geometry_invalid_or_empty'] += 1
            continue
        categories = []
        if tags.get('highway') and el.get('type') == 'way':
            categories.append('vias')
        if is_green(tags) and geom.geom_type in ('Polygon', 'MultiPolygon'):
            categories.append('areas_verdes')
        if is_equipment(tags):
            categories.append('equipamentos_candidatos')
        for cat in categories:
            key = (el.get('type'), el.get('id'))
            if key in seen[cat]:
                continue
            g = geom
            if cat == 'vias':
                g = geom.boundary if geom.geom_type in ('Polygon', 'MultiPolygon') else geom
                g = g.intersection(clipping)
            elif cat == 'areas_verdes':
                g = geom.intersection(clipping)
            else:
                # Edifício/terreno vira um ponto de representação, NÃO uma entrada de acesso.
                if geom.geom_type != 'Point':
                    g = geom.representative_point()
                if not clipping.covers(g):
                    continue
            if g.is_empty or not g.is_valid:
                continue
            if cat == 'vias' and g.geom_type not in ('LineString', 'MultiLineString'):
                continue
            if cat == 'areas_verdes' and (g.geom_type not in ('Polygon', 'MultiPolygon') or g.area == 0):
                continue
            props = {
                'osm_id': el.get('id'),
                'osm_type': el.get('type'),
                'nome': tags.get('name', ''),
                'classe_osm': tags.get('highway') or tags.get('leisure') or tags.get('amenity') or tags.get('office') or tags.get('landuse') or tags.get('natural'),
                'origem': 'OpenStreetMap',
                'tags_osm': tags,
            }
            if cat == 'equipamentos_candidatos':
                props['gestao_publica_verificada'] = False
                props['observacao'] = 'Candidato por classificação OSM. Confirmar natureza pública em fonte oficial.'
                props['posicao'] = 'geometria_original' if geom.geom_type == 'Point' else 'ponto_representativo_da_geometria'
            result[cat].append({'type': 'Feature', 'geometry': mapping(g), 'properties': props})
            seen[cat].add(key)
    return result, skipped


def main():
    print('Consultando OpenStreetMap via Overpass (dados reais)...')
    response, api = download(overpass_query())
    features, skipped = extract_features(response)
    if not features['vias'] or not features['areas_verdes'] or not features['equipamentos_candidatos']:
        print('AVISO: há uma ou mais camadas sem feições. Inspecione os dados e a cobertura.')
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    # Grava somente após resposta real. Nenhuma camada simulada.
    fetched_at = datetime.now(timezone.utc).isoformat()
    (RAW / 'osm_resposta.json').write_text(json.dumps(response, ensure_ascii=False), encoding='utf-8')
    for layer, vals in features.items():
        fc = {'type': 'FeatureCollection', 'features': vals}
        (OUT / f'{layer}.geojson').write_text(json.dumps(fc, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'{layer}: {len(vals)} feições')
    meta = {
        'consulta_utc': fetched_at,
        'overpass_endpoint': api,
        'osm_base_timestamp': response.get('osm3s', {}).get('timestamp_osm_base'),
        'recorte_bbox_wgs84': list(BBOX),
        'recorte_tipo': 'caixa de estudo, não limite oficial do bairro Centro',
        'licenca': 'OpenStreetMap contributors / ODbL',
        'contagem': {k: len(v) for k, v in features.items()},
        'ignorados': skipped,
        'observacoes': ['Equipamentos são candidatos; situação de gestão pública não verificada.',
                        'Feições ausentes no OSM não significam ausência no território.'],
    }
    (ROOT / 'documentacao' / 'relatorio_coleta.json').write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Concluído. Execute: python scripts/validar_geojson.py')


if __name__ == '__main__':
    main()
