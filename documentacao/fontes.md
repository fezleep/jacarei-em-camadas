# fontes, extração e limitações

## OpenStreetMap

as geometrias deste projeto foram coletadas do [OpenStreetMap](https://www.openstreetmap.org/) pela [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API).

- coleta: `2026-10-22T13:33:48.673863+00:00`;
- timestamp informado pela base OSM: `2026-10-22T13:32:01Z`;
- endpoint que respondeu à coleta: `https://overpass-api.de/api/interpreter`;
- recorte WGS 84: `(-45.9750, -23.3060, -45.9600, -23.2960)`.

os filtros completos estão em `scripts/baixar_osm.py`. a coleta produziu 334 vias, 14 áreas verdes e 25 equipamentos candidatos. os GeoJSON foram validados depois da extração.

dados: © OpenStreetMap contributors. licença: [Open Database License — ODbL](https://www.openstreetmap.org/copyright). os arquivos em `dados/processados/` são uma base derivada e continuam sujeitos à ODbL.

## camadas

- `vias.geojson`: elementos com tag `highway`;
- `areas_verdes.geojson`: polígonos selecionados por tags como `leisure`, `landuse` e `natural`;
- `equipamentos_candidatos.geojson`: pontos derivados de tags `amenity` e `office` selecionadas pelo coletor.

a presença de uma tag `amenity` não comprova gestão pública. por isso, a terceira camada usa o nome “equipamentos candidatos”. pontos derivados de edifícios representam uma posição dentro do polígono, não a entrada oficial.

## recorte

o retângulo de estudo foi escolhido para o piloto da região central. ele não é o limite oficial do bairro Centro e não deve ser usado como delimitação administrativa.

feições podem estar incompletas nas bordas. ausências no OpenStreetMap também não significam ausência no território. as contagens não formam um inventário oficial e não medem cobertura ou acessibilidade.

## fontes de conferência

o [portal GeoJacareí](https://geosegovplan.jacarei.sp.gov.br/geojacarei/mapas2022/index.html) e páginas públicas da Prefeitura foram usados apenas como referências de contexto. nenhuma geometria municipal foi copiada ou redistribuída neste repositório.
