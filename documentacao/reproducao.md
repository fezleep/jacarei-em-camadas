# reprodução do projeto

## validação dos dados

com Python 3.11 ou mais recente, a partir da raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\validar_geojson.py
```

em Linux ou macOS, use `.venv/bin/python` no lugar do executável dentro de `Scripts`.

## abertura no QGIS

abra `qgis/jacarei_em_camadas_centro_portfolio_publicacao.qgz` no QGIS 3.44 LTR ou versão compatível. o projeto usa `EPSG:31983` e caminhos relativos para:

- `../dados/processados/vias.geojson`;
- `../dados/processados/areas_verdes.geojson`;
- `../dados/processados/equipamentos_candidatos.geojson`;
- `simbolos/seta_norte.svg`.

por isso, a estrutura das pastas deve ser mantida depois do clone.

## nova coleta

`scripts/baixar_osm.py` consulta a Overpass API e substitui os arquivos em `dados/processados/`. como o OpenStreetMap muda ao longo do tempo, uma nova coleta não é uma reprodução byte a byte desta versão e pode alterar geometrias e contagens.

```powershell
.\.venv\Scripts\python.exe scripts\baixar_osm.py
.\.venv\Scripts\python.exe scripts\validar_geojson.py
```

## scripts PyQGIS

os scripts de montagem e acabamento importam `qgis.core` e devem ser executados pelo Python do QGIS ou pelo editor do Console Python do QGIS Desktop:

- `scripts/montar_qgis.py` cria o projeto inicial;
- `scripts/finalizar_mapa_portfolio.py` monta o primeiro layout de portfólio;
- `scripts/revisar_mapa_portfolio_v2.py` aplica a revisão visual v2;
- `scripts/preparar_qgis_publicacao.py` cria a cópia portátil usada no repositório.

esses scripts preservam as fontes GeoJSON. as etapas de acabamento interrompem a execução quando o arquivo de saída já existe, evitando sobrescrita acidental.

## ambiente validado nesta entrega

- QGIS LTR 3.44.14 “Solothurn”;
- Python 3.12 para coleta e testes;
- projeto em SIRGAS 2000 / UTM zona 23S (`EPSG:31983`);
- GeoJSON em WGS 84 (`EPSG:4326`).
