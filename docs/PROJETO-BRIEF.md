# Brief do Projeto — Observatório Rural Paranaense

> Contexto compartilhado e fonte da verdade para qualquer pessoa (ou agente) que
> escreva arquivos neste repositório. Mantém coerência entre páginas, docs e CI.

## O que é
Hub público de inteligência de dados da agropecuária e do desenvolvimento rural do
Paraná. Agrega o ecossistema de painéis dinâmicos do PR sob uma marca institucional,
com **dados abertos** (download + dicionário) como diferencial.

- **Repo / hub:** `observatorio-rural-parana.github.io` (GitHub Pages), em **org dedicada `observatorio-rural-parana`**, até haver domínio `.pr.gov.br`.
- **Modelo de referência:** Observatório Agro Catarinense (Cepa/Epagri).
- **Sistema-fonte:** SEAGRI-PR = SEAB · IDR-Paraná · CEASA-PR · ADAPAR.

## Decisões travadas (2026-05-29)
1. **Caráter institucional oficial** (IDR/SEAB) — marca de governo; equipe/fomento via Edital Push Innovation / FAPEAGRO; convênios formais de dados.
2. **Padronizar sob nova org antes de publicar** — cookiecutter de painel, stack unificada, dados abertos. Não é só linkar painéis.
3. **Design system único, pendor editorial** — base no estilo "jornal-creme" + verdes IDR (ver `assets/css/tokens.css`).
4. **Dados abertos: SIM** — CSV/XLSX/JSON + dicionário de dados por painel.

## Fonte da verdade (NÃO duplicar/divergir)
- **Cores, tipografia, espaçamento, sombra:** `assets/css/tokens.css`. Sempre `var(--…)`; nunca hex solto.
- **Taxonomia de eixos e painéis:** `assets/data/eixos.json` (11 eixos + 2 camadas contextuais + núcleo de inteligência). 5 eixos-piloto: `desempenho-economico`, `mercado-precos`, `comercio-exterior`, `credito-politicas`, `ater`.
- **Geo:** chave única `regional_idr` (399 municípios → 23 regionais → 7 mesorregiões). De-para em `assets/data/geo/municipios_ref_idr.csv`; mapa por núcleo em `assets/data/geo/pr_nucleos_regionais.json`. Ver `docs/GEO.md`.
- **Logos oficiais:** `assets/logos/` (idr-horizontal/vertical, gov-seab-horizontal/vertical, + `logos_b64.json`).

## Identidade visual (resumo dos tokens)
- Papel creme `--paper #f4f1ea`; tinta ardósia `--ink #1d2529`.
- Marca primária verde IDR `--green #008854` / `--green-d #0a5e3d`.
- Azul institucional Gov-PR `--azul #0079bb`; assinatura em gradiente azul→verde `--sig`.
- Acentos: olive, amber (atenção), clay/vermelho (alerta).
- Serif **Georgia** (títulos/destaques editoriais) + Sans **Segoe UI** (corpo/UI) + Mono **Consolas** (números).
- Largura máx. `--maxw 1180px`. Editorial, sóbrio, imprimível, acessível (WCAG AA).

## Ecossistema reutilizável (resumo)
Família `avnergomes` (React 18 + Vite + Tailwind + Recharts/D3 + Leaflet; ETL Python→JSON estático; GitHub Pages): vbp-parana, precos-diarios (+API Flask), precos-florestais, precos-de-terras, comexstat-parana, credito-rural-parana, emprego-agro-parana, censo-parana, carne_madeira; contextuais saude-parana, seguranca-parana; geo aguasegura/psh/BI-psh/prns; ATER rededeaterparana/rtv; núcleo c2-parana; molde de hub `datageoparana.github.io`.

## Convenções de autoria
- HTML/CSS/JS **vanilla** (sem framework) no hub; sites estáticos GitHub Pages; `.nojekyll` presente.
- Idioma de conteúdo: **pt-BR**. Acessibilidade: landmarks, `alt`, foco visível (`--focus-ring`), contraste AA.
- SEO/IA: cada página com `<title>`, meta description, Open Graph, JSON-LD quando aplicável; `robots.txt`, `sitemap.xml`, `llms.txt`.
- Toda cor/tipo via tokens. Toda lista de painéis lida de `eixos.json` (não hardcodar painel em HTML).
- Atribuição de fontes sempre explícita (transparência/reprodutibilidade).
