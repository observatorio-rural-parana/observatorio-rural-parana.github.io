# Roadmap — Observatório Rural Paranaense

> Plano de evolução em fases, com checkboxes de status. Fonte da verdade para
> sequenciamento de trabalho. Decisões, convenções e identidade visual vêm de
> [`PROJETO-BRIEF.md`](./PROJETO-BRIEF.md), [`../assets/css/tokens.css`](../assets/css/tokens.css)
> e [`../assets/data/eixos.json`](../assets/data/eixos.json) — **não duplicar nem divergir** deles.

**Última revisão:** 2026-05-29 · **Estado atual:** Fase 0 (Fundação) em andamento.

## Como ler este documento

- `[x]` concluído · `[~]` em andamento / parcial · `[ ]` a fazer.
- **🚧 Bloqueante** = item que trava o avanço de uma fase inteira.
- **🔗 Depende de** = pré-requisito explícito de outro item.
- Os 5 **eixos-piloto** (marcados `piloto: true` em `eixos.json`) guiam a Fase 1:
  `desempenho-economico`, `mercado-precos`, `comercio-exterior`, `credito-politicas`, `ater`.
- Nenhum painel é hardcodado aqui: a lista canônica está em `eixos.json`.

---

## Visão geral das fases

| Fase | Objetivo | Marco de conclusão |
|------|----------|--------------------|
| 0 — Fundação | Repositório, design system, taxonomia, governança técnica no ar | Hub publicado em GitHub Pages sob a org dedicada |
| 1 — Cookiecutter + 5 eixos-piloto | Stack unificada e padronização dos painéis-piloto com dados abertos + dicionário | 5 eixos-piloto padronizados e com download de dados |
| 2 — Hub completo | Navegação por eixo, embed de painéis, catálogo de dados, páginas institucionais | Hub navegável e indexável, com catálogo de dados abertos |
| 3 — Publicações | Templates editoriais unificados, pipeline e cadência de boletins/sínteses | Primeiro boletim e síntese anual publicados pelo pipeline |
| 4 — Expansão | Novos eixos (sanidade, clima, hídrico, infra/biogás) e núcleo de inteligência | Eixos restantes de `eixos.json` cobertos; `c2-parana` integrado |
| T — Transversal | Segurança, LGPD e convênios atravessando todas as fases | Convênios formais e conformidade LGPD vigentes |

---

## 🚧 Bloqueantes globais

Estes itens travam a publicação e/ou a oficialização; resolvê-los destrava fases inteiras.

- [ ] **Criar a org GitHub `observatorio-rural-parana`** (decisão travada no brief). 🚧 _Bloqueia Fase 0 (push/Pages) e toda publicação._
- [ ] **Marca/identidade oficial autorizada (IDR/SEAB)** — uso institucional de logos e wordmarks. 🚧 _Bloqueia comunicação como portal de governo (Fase 2)._
- [ ] **Convênios formais de dados** (SEAB · IDR-Paraná · CEASA-PR · ADAPAR). 🚧 _Bloqueia microdados restritos da Fase 4 e a publicação de séries sensíveis._
- [ ] **Equipe/fomento** via Edital Push Innovation / FAPEAGRO (sustentação e cadência). 🚧 _Bloqueia a cadência recorrente da Fase 3._

---

## Fase 0 — Fundação

> Base do repositório, design system e governança técnica. A maior parte já existe;
> falta sair da máquina local para a org e para o GitHub Pages.

### Já existe (concluído)

- [x] Repositório Git inicializado (`.git/`).
- [x] Design system único em [`assets/css/tokens.css`](../assets/css/tokens.css) — cores, tipografia, espaçamento, sombra, movimento (sempre `var(--…)`).
- [x] Taxonomia de eixos/painéis em [`assets/data/eixos.json`](../assets/data/eixos.json) — 11 eixos + 2 camadas contextuais + núcleo de inteligência.
- [x] Brief/fonte da verdade em [`docs/PROJETO-BRIEF.md`](./PROJETO-BRIEF.md).
- [x] Logos oficiais em [`assets/logos/`](../assets/logos/): `idr-horizontal.png`, `idr-vertical.png`, `gov-seab-horizontal.png`, `gov-seab-vertical.png` + `logos_b64.json`.
- [x] Geo de-para: [`assets/data/geo/municipios_ref_idr.csv`](../assets/data/geo/municipios_ref_idr.csv) (399 municípios → 23 regionais → 7 mesorregiões, chave `regional_idr`) e [`assets/data/geo/pr_nucleos_regionais.json`](../assets/data/geo/pr_nucleos_regionais.json).
- [x] Dotfiles de Git LFS para malhas pesadas: [`.gitattributes`](../.gitattributes) (`mun_*.json`, `*.geojson`, `*.topojson`, `*.pmtiles`, `*.fgb`) + normalização de fim de linha.
- [x] `.gitignore` (segredos, build, ETL intermediário) e [`.nojekyll`](../.nojekyll) presentes.

### Falta concluir a fundação

- [ ] **Hub scaffold** — `index.html` da home + shell de layout (header com assinatura `--sig`, landmarks `header/nav/main/footer`, skip-link, foco visível via `--focus-ring`), consumindo `tokens.css` e lendo `eixos.json`. 🔗 Depende de: `tokens.css`, `eixos.json` (ambos prontos).
- [ ] **Docs de referência citados no brief** — criar `docs/GEO.md` (modelo geo + LFS) e `docs/ARQUITETURA.md` (inclui §Segurança citada por `.gitignore` e pelo núcleo `c2-parana`). 🔗 GEO.md é pré-requisito para o uso correto das malhas LFS.
- [ ] **CI** — workflow em `.github/workflows/` ainda **não existe**: criar pipeline mínimo (validação de HTML/links, lint de `eixos.json`, link-check dos painéis `ativo`, checagem de `tokens.css` sem hex solto). 🔗 Depende de: hub scaffold.
- [ ] **SEO/IA base** — `robots.txt`, `sitemap.xml`, `llms.txt` (convenção do brief). 🔗 Depende de: hub scaffold.
- [ ] **`git lfs install`** executado e malha municipal (~50 MB) rastreada por LFS antes do primeiro push. 🔗 Depende de: org criada. _(executar manualmente — fora do escopo de escrita de arquivos.)_
- [ ] **Criar a org GitHub `observatorio-rural-parana`.** 🚧 _Ver Bloqueantes globais._
- [ ] **Push do repositório** para a org + configurar remoto. 🔗 Depende de: org criada, `git lfs install`.
- [ ] **Ativar GitHub Pages** (branch/raiz, `.nojekyll` já presente). 🔗 Depende de: push.

**Saída da Fase 0:** hub público no ar em `observatorio-rural-parana.github.io`, com design system, taxonomia e CI ativos.

---

## Fase 1 — Cookiecutter + padronização dos 5 eixos-piloto

> "Não é só linkar painéis" (decisão travada). Criar um **cookiecutter de painel** que
> impõe stack unificada, design system e **dados abertos** (CSV/XLSX/JSON + dicionário),
> e aplicá-lo aos 5 eixos-piloto.

### Cookiecutter / stack unificada

- [ ] **Template de painel (cookiecutter)** alinhado à família `avnergomes` (React 18 + Vite + Tailwind + Recharts/D3 + Leaflet; ETL Python → JSON estático; deploy GitHub Pages). 🔗 Depende de: `tokens.css` exportado como camada de marca consumível pelos painéis.
- [ ] **Ponte de design system** — tokens do hub disponíveis aos painéis (camada CSS/JSON de marca compartilhada) para coerência visual.
- [ ] **Contrato de dados abertos** — convenção de pastas (`/data` publicado vs. `data/raw`/`data/tmp` ignorados), formatos (CSV/XLSX/JSON) e **dicionário de dados** por painel (esquema padrão de colunas, unidades, fonte, periodicidade).
- [ ] **Chave geográfica padronizada** — todos os painéis usam `regional_idr` e o de-para de `assets/data/geo/` (sem geocódigos divergentes). 🔗 Depende de: `docs/GEO.md`.
- [ ] **Atribuição de fontes obrigatória** em cada painel (transparência/reprodutibilidade, conforme brief).

### Padronização dos eixos-piloto (`eixos.json` → `piloto: true`)

- [ ] **`desempenho-economico` — VBP** (`vbp-parana`): padronizar ao cookiecutter + dados abertos + dicionário. Indicador-âncora (partilha de ICMS). Fontes: DERAL/SEAB, IBGE, IPARDES.
- [ ] **`mercado-precos`** — padronizar os 3 painéis ativos: Preços diários/SIMA (+ API Flask/Render), Preços florestais (1997–2025), Preços de terras/SIPT (1998–2025). Dados abertos + dicionário por painel. Fontes: DERAL/SIMA, CEASA-PR, DEFLOP, SIPT.
- [ ] **`comercio-exterior`** (`comexstat-parana`): padronizar + dados abertos + dicionário. Fonte: MDIC/ComexStat (filtro PR).
- [ ] **`credito-politicas`** (`credito-rural-parana`, SICOR): padronizar + dados abertos + dicionário. Fontes: BCB/SICOR, SEAB/DPA. ⚠️ Painel LC-CD (Compra Direta & Leite das Crianças) é `interno` — **só agregados** no portal público (cruza CPF/CNPJ). 🔗 Ver Transversal/LGPD.
- [ ] **`ater`** — padronizar Rede Paranaense de ATER (`rededeaterparana`) e RTV (`rtv`) + dados abertos + dicionário. Fonte: IDR-Paraná (SISATER/GETEC).
- [ ] **Dicionário de dados consolidado** dos 5 eixos-piloto, linkado a partir de cada painel.

**Saída da Fase 1:** 5 eixos-piloto rodando sobre o cookiecutter, com download de dados + dicionário e identidade visual coerente.

---

## Fase 2 — Hub completo

> Tornar o hub navegável, indexável e útil como portal de inteligência, com o
> **catálogo de dados abertos** como diferencial frente ao modelo de referência (Cepa/Epagri).

- [ ] **Navegação por eixo** gerada a partir de `eixos.json` (11 eixos + camadas contextuais + núcleo), respeitando `ordem` e `status_legenda`.
- [ ] **Embed de painéis** — páginas de eixo com incorporação dos painéis `ativo` (iframe responsivo + link externo + atribuição de fonte), lendo `url` de `eixos.json`. 🔗 Depende de: Fase 1 (painéis padronizados).
- [ ] **Catálogo de dados abertos** — índice navegável/filtrável de todos os datasets (download + dicionário), agregando os contratos de dados da Fase 1.
- [ ] **Página Arquitetura** (`docs/ARQUITETURA.md` + página pública) — stack, fluxo ETL → JSON estático, modelo geo, §Segurança.
- [ ] **Página Metodologia** — critérios de cálculo, periodicidade, definições (ex.: VBP, VAB).
- [ ] **Página Fontes** — relação completa de fontes por eixo (DERAL/SEAB, IBGE, IPARDES, CEASA-PR, MDIC/ComexStat, BCB/SICOR, IDR, etc.), com atribuição explícita.
- [ ] **SEO/IA por página** — `<title>`, meta description, Open Graph, JSON-LD quando aplicável; `sitemap.xml` atualizado.
- [ ] **Acessibilidade WCAG AA** auditada em todas as páginas (landmarks, `alt`, foco visível, contraste — tokens já AA).
- [ ] **i18n (opcional)** — estrutura para PT/EN/ES; ativar somente se houver demanda institucional. _(não bloqueante.)_

**Saída da Fase 2:** hub completo, navegável por eixo, com catálogo de dados e páginas institucionais.

---

## Fase 3 — Publicações

> Unificar o pendor editorial (base "jornal-creme" + verdes IDR) em templates de
> publicação reaproveitáveis e estabelecer cadência editorial.

- [ ] **Unificar templates editoriais** — consolidar os geradores **LC-CD** (origem do design system, ver cabeçalho de `tokens.css`) e **cibiogás** sob o design system único (`tokens.css`), sem cores/tipos fora dos tokens.
- [ ] **Template de boletim** (web + imprimível, `@media print` já previsto nos tokens) reutilizável por eixo.
- [ ] **Template de síntese anual** (panorama do agro paranaense).
- [ ] **Pipeline de publicação** — fluxo de dados → publicação (gerar HTML/PDF a partir dos datasets abertos da Fase 1), versionado e reproduzível, integrado ao CI.
- [ ] **Cadência de boletim** definida e operada (periodicidade por eixo). 🔗 Depende de: equipe/fomento (Bloqueante global).
- [ ] **Cadência de síntese anual** definida e operada. 🔗 Depende de: equipe/fomento.
- [ ] **Primeiro boletim publicado** pelo pipeline (marco da fase).

**Saída da Fase 3:** templates editoriais unificados e cadência de publicação ativa (boletim + síntese anual).

---

## Fase 4 — Expansão

> Cobrir os eixos restantes de `eixos.json` (`piloto: false`/`planejado`) e integrar o
> núcleo de inteligência territorial.

- [ ] **`sanidade-defesa` (ADAPAR)** — integrar/espelhar painéis públicos da ADAPAR (GTA/PTV, agrotóxicos/SIAGRO, pragas georreferenciadas); microdados via LAI. 🔗 Depende de: convênio ADAPAR (Bloqueante global).
- [ ] **`clima-agrometeorologia` (IDR)** — painel Agroclima Paraná (boletins, desvios, alertas de geada/estiagem/calor). Fontes: IDR Agrometeorologia, SIMEPAR, INMET.
- [ ] **`recursos-hidricos-ambiental`** — consolidar painéis hídricos/ambientais ativos (`aguasegura`, `psh`, `prns`) ao hub e completar com CAR/uso do solo/MapBiomas. 🔗 Depende de: malhas LFS (Fase 0).
- [ ] **`infraestrutura-energia` — biogás** — portar a base **cibiogás** (local) como painel + publicação (Panorama do Biogás no PR). Fontes: SEAB, ADAPAR, IBGE/PPM, CIBIOGÁS.
- [ ] **`producao-agropecuaria`** — completar painel de produção vegetal e pecuária (ao lado do ILPF `carne_madeira` já ativo). Fontes: IBGE LSPA/PAM/PPM/Censo, DERAL.
- [ ] **`desenvolvimento-rural`** — consolidar `censo-parana` e `emprego-agro-parana` ao hub.
- [ ] **Camadas contextuais** — integrar `saude-parana` e `seguranca-parana` como contexto rural (status `contextual`).
- [ ] **Núcleo `c2-parana`** (Inteligência Territorial, índice IRTC, 399 municípios) — integrar **somente após**: rotação de secrets, remoção de gating e de dados sintéticos hardcoded (ver `docs/ARQUITETURA.md §Segurança`). 🚧 _Bloqueante específico do núcleo._ 🔗 Ver Transversal/Segurança.

**Saída da Fase 4:** todos os eixos de `eixos.json` cobertos e núcleo de inteligência integrado com segurança.

---

## Fase Transversal — Segurança, LGPD e Convênios

> Atravessa todas as fases. Itens aqui condicionam o que pode ser publicado.

### Segurança

- [ ] **Nenhum segredo versionado** — `.gitignore` cobre `.env*`, `*.secret`, `config.local.js`; validar no CI.
- [ ] **Rotação de secrets** do `c2-parana` antes de qualquer integração. 🚧 _Bloqueia Fase 4 (núcleo)._
- [ ] **Remoção de gating e de dados sintéticos hardcoded** no `c2-parana`. 🔗 Ver `docs/ARQUITETURA.md §Segurança`.
- [ ] **Política de segurança documentada** em `docs/ARQUITETURA.md §Segurança` (citada por `.gitignore` e por `eixos.json`).

### LGPD

- [ ] **Só agregados** no portal público para bases que cruzam CPF/CNPJ (LC-CD: Compra Direta & Leite das Crianças — `status: interno` em `eixos.json`). 🚧 _Bloqueia publicação granular do eixo `credito-politicas`._
- [ ] **Microdados restritos via LAI** (ex.: ADAPAR) tratados fora do portal público; portal expõe apenas agregados. 🔗 Ver Fase 4.
- [ ] **Classificação de dados** por painel (público / agregado / interno) registrada no contrato de dados.

### Convênios

- [ ] **Convênios formais de dados** com SEAB, IDR-Paraná, CEASA-PR e ADAPAR. 🚧 _Bloqueante global._
- [ ] **Autorização de marca** (IDR/SEAB) para uso institucional oficial. 🚧 _Bloqueante global._

---

## Resumo de dependências críticas

- **Org GitHub** → habilita push, Pages e toda publicação (Fase 0 → tudo).
- **`git lfs install`** → habilita malhas geográficas pesadas (Fase 0 → Fase 4 hídrico).
- **Cookiecutter + contrato de dados** (Fase 1) → habilita embeds, catálogo (Fase 2) e pipeline de publicação (Fase 3).
- **Equipe/fomento** → habilita cadência editorial recorrente (Fase 3).
- **Convênios + marca oficial** → habilitam oficialização (Fase 2) e eixos sensíveis (Fase 4).
- **Segurança do `c2-parana`** (rotação de secrets, remoção de gating/dados sintéticos) → habilita o núcleo de inteligência (Fase 4).
