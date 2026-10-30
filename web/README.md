# aplicação web

primeira versão navegável de **jacareí em camadas**, construída com React, TypeScript, Vite e Leaflet.

## executar localmente

```powershell
cd web
npm ci
npm run dev
```

acesse `http://localhost:5173/jacarei-em-camadas/`.

## verificar

```powershell
npm run lint
npm run test
npm run build
npm run preview
```

a aplicação importa diretamente os três arquivos de `../dados/processados/`. eles permanecem como a única fonte a manter. o `base` do Vite está configurado para a publicação no GitHub Pages em `/jacarei-em-camadas/`.

os blocos cartográficos usam o serviço de tiles padrão do OpenStreetMap. qualquer publicação deve continuar respeitando a [política de uso de tiles](https://operations.osmfoundation.org/policies/tiles/) e preservar a atribuição visível.
