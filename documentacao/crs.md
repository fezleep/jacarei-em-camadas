# Coordenadas, CRS e métricas

- **GeoJSON**: armazena WGS 84 geográfico (`EPSG:4326`), coordenadas em **[longitude, latitude]** e unidades em **graus**. Isso facilita uso futuro no Leaflet e segue RFC 7946.
- **Projeto QGIS**: usa **SIRGAS 2000 / UTM zona 23S (`EPSG:31983`)**, em **metros**, apropriado para visualização métrica e análises locais em Jacareí.
- QGIS reprojeta as camadas em memória para mostrar no CRS do projeto; não é obrigatório salvar GeoJSON em EPSG:31983.
- **Semana 3:** um buffer de 500 m deve ser calculado em `EPSG:31983`; 500 m em linha reta não é distância de caminhada nem implica cobertura de serviço.

Referências: https://epsg.io/4326 , https://epsg.io/31983 , https://www.rfc-editor.org/rfc/rfc7946
