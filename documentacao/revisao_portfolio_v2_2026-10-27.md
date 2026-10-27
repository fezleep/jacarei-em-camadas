# Revisão da versão de portfólio — v2 — 27/10/2026

## Escopo

A revisão partiu de `qgis/jacarei_em_camadas_centro_portfolio.qgz` e não sobrescreveu o projeto nem as exportações aprovadas. Nenhuma geometria, camada, simbologia temática, extensão ou escala foi alterada.

## Alterações

1. O símbolo circular de norte foi substituído pelo `NorthArrow_04.svg` fornecido pelo QGIS, acompanhado da letra “N”. O símbolo permanece vinculado ao mapa, que tem rotação de 0°, e aponta corretamente para o topo.
2. O bloco de informações técnicas continua com 59 mm de largura. Título e corpo foram separados, com título em negrito, corpo ligeiramente menor e espaços entre fonte/licença, coleta, CRS e ressalva do recorte.
3. O PDF foi exportado com `forceVectorOutput=True`, `rasterizeWholeImage=False` e `TextRenderFormat.AlwaysText`.

## Arquivos

- `qgis/jacarei_em_camadas_centro_portfolio_v2.qgz`
- `mapas/jacarei_em_camadas_centro_portfolio_v2_300dpi.png`
- `mapas/jacarei_em_camadas_centro_portfolio_v2.pdf`
- `scripts/revisar_mapa_portfolio_v2.py`

## Validação

- Projeto e camadas: EPSG:31983; três fontes EPSG:4326; contagens preservadas em 334, 14 e 25 feições.
- Escala v1/v2: 1:7.455,786 nas duas versões; extensões idênticas.
- Painel técnico: 59 mm na v1 e na v2.
- PNG: 3507 × 2480 px, 300 DPI; revisão visual sem cortes, sobreposições ou perda aparente de legibilidade.
- PDF: `%PDF-1.4`, uma página, nove recursos de fonte, três mapas `ToUnicode`, 29 blocos e 608 operadores de texto. O conteúdo não é uma rasterização integral e permanece selecionável em leitores compatíveis.
- Os SHA-256 dos três arquivos aprovados permaneceram inalterados durante a revisão.

## Limitações

O ambiente não dispõe de `pdftotext`, `pdfinfo` ou biblioteca externa de leitura de PDF. A selecionabilidade foi validada pela configuração explícita do exportador e pela presença de fontes, mapas Unicode e operadores de texto no PDF. Recomenda-se uma conferência final de seleção/cópia no visualizador que será usado para publicação, pois leitores podem tratar fontes incorporadas de formas diferentes.

O QGIS 3.44 ainda aceita os métodos tipográficos usados, mas registra avisos de depreciação. O GDAL também emite uma mensagem não bloqueante durante a gravação do PNG; o arquivo resultante foi aberto e validado normalmente.
