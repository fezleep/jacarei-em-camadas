"""Testes com dados FICTÍCIOS somente em memória (não entram nas camadas reais)."""
import json
from pathlib import Path

from shapely.geometry import shape

from scripts.baixar_osm import BBOX, element_geometry, extract_features, overpass_query
from scripts.validar_geojson import validate_file


def p(lon, lat):
    return {'lon': lon, 'lat': lat}


def test_overpass_query_usa_bbox():
    query = overpass_query()
    assert '(-23.306,-45.975,-23.296,-45.96)' in query
    assert 'out center geom;' in query


def test_tres_camadas_e_recorte():
    sample = {'elements': [
        {'type': 'way', 'id': 1, 'tags': {'highway': 'residential', 'name': 'Rua sintética'},
         'geometry': [p(-45.971, -23.302), p(-45.969, -23.302)]},
        {'type': 'way', 'id': 2, 'tags': {'leisure': 'park', 'name': 'Parque sintético'},
         'geometry': [p(-45.972,-23.303),p(-45.971,-23.303),p(-45.971,-23.302),p(-45.972,-23.302),p(-45.972,-23.303)]},
        {'type': 'node', 'id': 3, 'tags': {'amenity': 'library', 'name': 'Biblioteca sintética'},
         'lon': -45.970, 'lat': -23.301},
    ]}
    result, _ = extract_features(sample)
    assert {k: len(v) for k,v in result.items()} == {'vias':1, 'areas_verdes':1, 'equipamentos_candidatos':1}
    assert result['equipamentos_candidatos'][0]['properties']['gestao_publica_verificada'] is False
    for layer in result.values():
        assert shape(layer[0]['geometry']).is_valid


def test_validador_detecta_fora_recorte(tmp_path):
    obj = {'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[-46.0,-23.3]},'properties':{'osm_id':42}}]}
    path=tmp_path/'test.geojson'
    path.write_text(json.dumps(obj),encoding='utf8')
    count,errors=validate_file(path,{'Point'})
    assert count==1
    assert any('fora do recorte' in e for e in errors)


def test_polygon_way():
    g=element_geometry({'type':'way','geometry':[p(-45.970,-23.302),p(-45.969,-23.302),p(-45.969,-23.301),p(-45.970,-23.302)]})
    assert g.geom_type=='Polygon'
    assert g.is_valid
