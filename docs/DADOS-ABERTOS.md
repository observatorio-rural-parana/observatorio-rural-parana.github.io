# Dados Abertos — Especificação do Diferencial

> Fonte da verdade para **como** o Observatório Rural Paranaense publica dados abertos.
> Todo painel do ecossistema (ver `assets/data/eixos.json`) deve, além de visualizar,
> **entregar o dado**: download em formato aberto + dicionário + catálogo. É o
> diferencial declarado no brief (`docs/PROJETO-BRIEF.md`, decisão travada nº 4).
>
> **Convenções herdadas (não divergir):**
> - Conteúdo em **pt-BR**; sites estáticos GitHub Pages; ETL Python → arquivos estáticos.
> - Chave geográfica única **`regional_idr`** (399 municípios → 23 regionais → 7 mesorregiões).
>   De-para canônico em `assets/data/geo/municipios_ref_idr.csv` — ver `docs/GEO.md`.
> - Atribuição de fonte sempre explícita (transparência/reprodutibilidade).
> - LGPD: portal público só expõe **agregados**; nunca CPF/CNPJ (ver §6).

---

## Sumário

1. [Princípios](#1-principios)
2. [Esquema de dataset publicado + catálogo (`catalog.json`)](#2-esquema-de-dataset-publicado--catalogo)
3. [Dicionário de dados (template + exemplo VBP)](#3-dicionario-de-dados)
4. [Chave geográfica `regional_idr` e de-para](#4-chave-geografica-regional_idr)
5. [Publicação opcional no CKAN `dados.pr.gov.br`](#5-publicacao-opcional-no-ckan)
6. [Nota LGPD](#6-nota-lgpd)
7. [Checklist de publicação por painel](#7-checklist-de-publicacao-por-painel)

---

## 1. Princípios

Todo dado publicado segue estes princípios, alinhados aos **5★ Open Data** (Tim Berners-Lee)
e aos **princípios FAIR** (Findable, Accessible, Interoperable, Reusable).

| # | Princípio | Regra acionável |
|---|-----------|-----------------|
| P1 | **Todo painel publica seus dados** | Nenhuma visualização sem download. Cada painel expõe ao menos um dataset em `assets/data/{eixo}/` e o registra no `catalog.json`. Botão "Baixar dados" visível e acessível em todo painel. |
| P2 | **Formatos abertos** | Sempre **CSV** (UTF-8, sem BOM, separador `,`, decimal `.`) como formato canônico. **JSON** para consumo programático/web. **XLSX** opcional para conveniência de gestores (gerado a partir do CSV, nunca a fonte primária). Proibido publicar **só** PDF/imagem como dado. |
| P3 | **Licença aberta** | Padrão do portal: **CC BY 4.0** (atribuição). Dados de origem com licença distinta (ex.: termos do MDIC/BCB) preservam a licença de origem, declarada por dataset no campo `licenca`. |
| P4 | **Versionamento** | Versionar via Git (histórico audita cada mudança). Cada dataset carrega `versao` semântica (`MAJOR.MINOR`: MAJOR = mudança de esquema/colunas; MINOR = nova carga/período) e `ultima_atualizacao` (ISO 8601 `AAAA-MM-DD`). Snapshots imutáveis opcionais em `assets/data/{eixo}/_versions/{dataset}@{versao}.csv`. |
| P5 | **Atribuição de fonte** | Todo dataset declara `fonte` (origem primária do dado) e `orgao` (instituição responsável). Reproduzir transformações no ETL versionado; nunca publicar dado "órfão". |
| P6 | **Estável & rastreável** | `id` de dataset imutável (kebab-case). URLs de download estáveis e previsíveis (`assets/data/{eixo}/{dataset}.csv`). Quebra de esquema = bump de MAJOR + nota em `notas`. |
| P7 | **Acessível** | O dado é acessível por humanos (botão de download, dicionário em HTML/tabela) e por máquinas (`catalog.json`, JSON). Página de catálogo navegável por teclado, com landmarks e foco visível (WCAG AA). |

---

## 2. Esquema de dataset publicado + catálogo

### 2.1 Layout no repositório

Cada dataset vive sob o **`id` do eixo** (de `assets/data/eixos.json`, campo `eixos[].id`):

```
assets/data/
├── catalog.json                     ← manifesto único do portal (índice de tudo)
├── geo/
│   ├── municipios_ref_idr.csv       ← de-para geográfico canônico (ver §4)
│   └── pr_nucleos_regionais.json
├── desempenho-economico/            ← {eixo} = id do eixo em eixos.json
│   ├── vbp-municipios.csv           ← {dataset}.csv  (formato canônico)
│   ├── vbp-municipios.json          ← {dataset}.json (espelho p/ consumo web)
│   ├── vbp-municipios.xlsx          ← opcional
│   ├── vbp-municipios.dict.json     ← dicionário de dados (ver §3)
│   └── _versions/                   ← snapshots imutáveis opcionais
│       └── vbp-municipios@2.0.csv
├── mercado-precos/
│   └── …
└── comercio-exterior/
    └── …
```

**Regras de nomeação**
- `{eixo}`: exatamente um `id` existente em `eixos.json` (ex.: `desempenho-economico`, `mercado-precos`, `comercio-exterior`, `credito-politicas`, `ater`). Não inventar pasta fora da taxonomia.
- `{dataset}`: **kebab-case**, descritivo, estável (ex.: `vbp-municipios`, `precos-sima-diarios`). Vira o `id` no catálogo prefixado pelo eixo (`{eixo}/{dataset}`).
- Arquivos irmãos de um dataset compartilham o prefixo `{dataset}`: `.csv`, `.json`, `.xlsx`, `.dict.json`.

### 2.2 Manifesto de catálogo — `assets/data/catalog.json`

Índice único, lido por máquina, que descreve todos os datasets. A página pública de
dados abertos é renderizada **a partir deste arquivo** (não hardcodar dataset em HTML,
mesma regra de `eixos.json`).

**Esquema (campos por dataset):**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|:-----------:|-----------|
| `id` | string | sim | Identificador imutável `{eixo}/{dataset}` (kebab-case). |
| `titulo` | string | sim | Título legível em pt-BR. |
| `eixo` | string | sim | `id` do eixo em `eixos.json` (FK da taxonomia). |
| `descricao` | string | sim | O que o dataset contém, em uma a três frases. |
| `fonte` | string | sim | Origem primária do dado (ex.: "DERAL/SEAB — VBP"). |
| `orgao` | string | sim | Instituição responsável (ex.: "IDR-Paraná / SEAB"). |
| `periodicidade` | string | sim | Cadência de atualização: `anual` \| `mensal` \| `diaria` \| `semanal` \| `eventual` \| `unica`. |
| `ultima_atualizacao` | string (date) | sim | ISO 8601 `AAAA-MM-DD` da última carga. |
| `cobertura_temporal` | objeto | sim | `{ "inicio": "AAAA", "fim": "AAAA" }` (ou datas completas). |
| `cobertura_geografica` | objeto | sim | `{ "nivel": "regional_idr", "unidades": 23 }` — `nivel` ∈ `estado`\|`mesorregiao`\|`regional_idr`\|`municipio` (ver §4). |
| `formatos` | array\<string> | sim | Subconjunto de `["csv","json","xlsx"]`. `csv` sempre presente. |
| `arquivos` | array\<objeto> | sim | Lista `{ "formato", "url", "bytes", "sha256" }` — `url` relativa à raiz do site. `sha256` recomendado p/ integridade. |
| `licenca` | objeto | sim | `{ "id": "CC-BY-4.0", "nome": "Creative Commons Atribuição 4.0", "url": "https://creativecommons.org/licenses/by/4.0/deed.pt-br" }`. |
| `dicionario` | string (url) | sim | URL do `*.dict.json` do dataset (ver §3). |
| `versao` | string | sim | SemVer reduzido `MAJOR.MINOR` (ver P4). |
| `painel` | objeto | não | `{ "nome", "url" }` — painel que consome/visualiza o dataset (espelha `eixos.json`). |
| `notas` | string | não | Observações de carga, limitações, ressalvas LGPD. |

**Esqueleto do `catalog.json`:**

```json
{
  "$schema": "./catalog.schema.json",
  "portal": "Observatório Rural Paranaense",
  "licenca_padrao": {
    "id": "CC-BY-4.0",
    "nome": "Creative Commons Atribuição 4.0 Internacional",
    "url": "https://creativecommons.org/licenses/by/4.0/deed.pt-br"
  },
  "gerado_em": "2026-05-29",
  "datasets": [
    {
      "id": "desempenho-economico/vbp-municipios",
      "titulo": "Valor Bruto da Produção (VBP) por município — Paraná",
      "eixo": "desempenho-economico",
      "descricao": "VBP da agropecuária por município, ano e produto, em reais correntes. Indicador-âncora da partilha do ICMS estadual.",
      "fonte": "DERAL/SEAB — Valor Bruto da Produção Agropecuária",
      "orgao": "IDR-Paraná / SEAB",
      "periodicidade": "anual",
      "ultima_atualizacao": "2026-05-29",
      "cobertura_temporal": { "inicio": "2012", "fim": "2024" },
      "cobertura_geografica": { "nivel": "municipio", "unidades": 399 },
      "formatos": ["csv", "json", "xlsx"],
      "arquivos": [
        { "formato": "csv",  "url": "/assets/data/desempenho-economico/vbp-municipios.csv",  "bytes": null, "sha256": null },
        { "formato": "json", "url": "/assets/data/desempenho-economico/vbp-municipios.json", "bytes": null, "sha256": null },
        { "formato": "xlsx", "url": "/assets/data/desempenho-economico/vbp-municipios.xlsx", "bytes": null, "sha256": null }
      ],
      "licenca": {
        "id": "CC-BY-4.0",
        "nome": "Creative Commons Atribuição 4.0 Internacional",
        "url": "https://creativecommons.org/licenses/by/4.0/deed.pt-br"
      },
      "dicionario": "/assets/data/desempenho-economico/vbp-municipios.dict.json",
      "versao": "2.0",
      "painel": {
        "nome": "VBP do Paraná (2012–2024)",
        "url": "https://avnergomes.github.io/vbp-parana/"
      },
      "notas": "Valores em reais correntes (não deflacionados). Produtos agregados pela classificação DERAL."
    }
  ]
}
```

> **Validação (boundary):** validar `catalog.json` contra um JSON Schema (`catalog.schema.json`)
> no CI antes de publicar — `eixo` deve existir em `eixos.json`; `arquivos[].url` deve apontar
> para arquivo presente no repo; `cobertura_geografica.nivel` ∈ enum. Falhar rápido com mensagem clara.

---

## 3. Dicionário de dados

Cada dataset tem um dicionário **legível por humano e por máquina**, salvo como
`{dataset}.dict.json` ao lado dos dados. A página de dados abertos renderiza a tabela
abaixo a partir dele.

### 3.1 Template (uma linha por coluna)

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `nome_coluna` | `inteiro` \| `texto` \| `decimal` \| `data` \| `booleano` | unidade física (`R$`, `ha`, `t`, `%`, `—`) | o que a coluna representa | valores válidos / faixa / enum / FK | origem específica da coluna | ressalvas, precisão, nulos |

**Tipos canônicos:** `inteiro`, `decimal`, `texto`, `data` (ISO `AAAA-MM-DD`), `ano` (`AAAA`), `booleano`, `codigo` (string de código, ex. `cod_ibge`).

**Representação em máquina (`{dataset}.dict.json`):**

```json
{
  "dataset": "desempenho-economico/vbp-municipios",
  "titulo": "Dicionário — VBP por município",
  "versao": "2.0",
  "colunas": [
    {
      "coluna": "cod_ibge",
      "tipo": "codigo",
      "unidade": "—",
      "descricao": "Código IBGE do município (7 dígitos).",
      "dominio": "399 municípios do PR; FK → geo/municipios_ref_idr.csv (cod_ibge)",
      "fonte": "IBGE — Malha Municipal",
      "notas": "Chave primária junto de (ano, produto)."
    }
  ]
}
```

### 3.2 Exemplo preenchido — painel **VBP** (`desempenho-economico/vbp-municipios`)

Dataset plausível: VBP da agropecuária por município, ano e produto, em reais correntes.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `cod_ibge` | `codigo` | — | Código IBGE do município (7 dígitos). | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE — Malha Municipal | Compõe a chave primária `(cod_ibge, ano, produto)`. |
| `municipio` | `texto` | — | Nome do município (com acentuação oficial IBGE). | Texto livre controlado pelo de-para geográfico. | IBGE | Redundante com `cod_ibge`; mantido por legibilidade. Não usar como chave de join. |
| `regional_idr` | `codigo` | — | Núcleo Regional do IDR-Paraná a que o município pertence. | 23 regionais; FK → `geo/municipios_ref_idr.csv` (`reg_idr`). | IDR-Paraná | Derivado no ETL a partir de `cod_ibge` (ver §4). Chave de agregação regional. |
| `ano` | `ano` | ano | Ano de referência do VBP. | `2012`–`2024`. | DERAL/SEAB | Ano-safra/calendário conforme metodologia DERAL. |
| `produto` | `texto` | — | Produto agropecuário (classificação DERAL). | Ex.: `Soja`, `Milho`, `Frango`, `Leite`, `Feijão`, `Trigo`, `Bovinos`, `Suínos`. | DERAL/SEAB | Domínio fechado publicado em `vbp-municipios.produtos.csv`. |
| `vbp_reais` | `decimal` | R$ | Valor Bruto da Produção do produto no município/ano. | ≥ 0; reais correntes (não deflacionado). | DERAL/SEAB | Pode haver supressão por sigilo; ver `notas` do dataset. Decimal com ponto, sem separador de milhar. |

> Observação metodológica obrigatória no dicionário do VBP: valores em **reais correntes**;
> para séries comparáveis, deflacionar fora do dataset (deflator não embutido).

---

## 4. Chave geográfica `regional_idr`

A chave de junção territorial canônica do observatório é **`regional_idr`** — ver `docs/GEO.md`
(fonte da verdade geográfica) e o brief (`docs/PROJETO-BRIEF.md`).

- **Hierarquia:** 399 municípios → 23 regionais (`regional_idr`) → 7 mesorregiões → estado.
- **De-para canônico:** `assets/data/geo/municipios_ref_idr.csv`, com colunas:

  | coluna do de-para | papel | mapeia para |
  |-------------------|-------|-------------|
  | `cod_ibge` | código IBGE do município (7 díg.) | chave de join municipal |
  | `municipio` | nome oficial IBGE | rótulo |
  | `creg_idr` | código do núcleo regional IDR | identificador estável da regional |
  | `reg_idr` | nome do núcleo regional IDR | rótulo de `regional_idr` |
  | `meso_idr` | mesorregião IDR | nível superior de agregação |

- **Regra para datasets:** todo dataset com granularidade municipal carrega `cod_ibge`
  (chave forte) e **deve** poder derivar `regional_idr` via join com o de-para. Datasets
  publicados já em nível regional usam `regional_idr` diretamente como chave.
- **Não duplicar** o de-para dentro dos datasets de domínio: derivar no ETL a partir de
  `geo/municipios_ref_idr.csv`. Mudou um vínculo município→regional? Atualiza-se **só** o de-para.
- No `catalog.json`, declarar o nível em `cobertura_geografica.nivel`
  (`estado` | `mesorregiao` | `regional_idr` | `municipio`).

> Mapa/geometria das regionais: `assets/data/geo/pr_nucleos_regionais.json`. Detalhes,
> normalização de nomes e tratamento de fronteiras: **`docs/GEO.md`**.

---

## 5. Publicação opcional no CKAN

Além do download estático no GitHub Pages (canal primário), um dataset pode ser
**espelhado** no portal estadual **CKAN `dados.pr.gov.br`** quando houver convênio formal
de dados (ver brief, decisão nº 1). O GitHub Pages permanece a fonte versionada; o CKAN é
réplica de distribuição.

**Mapeamento `catalog.json` → CKAN (Dataset/Resource):**

| Campo no `catalog.json` | Campo CKAN (dataset/resource) |
|-------------------------|-------------------------------|
| `id` (`{eixo}/{dataset}`) | `name` (slug; barra → hífen) |
| `titulo` | `title` |
| `descricao` | `notes` |
| `orgao` | `organization` |
| `fonte` | `extras: fonte` |
| `eixo` | `groups` / tag de eixo |
| `licenca.id` | `license_id` (ex.: `cc-by`) |
| `ultima_atualizacao` | `metadata_modified` / `extras: ultima_atualizacao` |
| `cobertura_temporal` | `extras: temporal_coverage` |
| `cobertura_geografica` | `extras: spatial_coverage` (`regional_idr`) |
| `arquivos[]` | um **resource** por formato (`url`, `format`, `hash` = `sha256`) |
| `dicionario` | resource adicional (`format: JSON`, rótulo "Dicionário de dados") |

**Diretrizes de publicação CKAN**
- Sincronizar via API CKAN (`package_create` / `package_update`) a partir do `catalog.json`,
  em job manual/agendado — **fora** do build do Pages (não acoplar). Idempotente por `name`.
- Resource aponta para a **URL estável** no GitHub Pages (CKAN como índice federado), ou
  faz upload do arquivo quando o convênio exigir cópia hospedada.
- Token/credencial CKAN **somente** via variável de ambiente/secret no runner; nunca no repo
  (ver `assets/css/tokens.css`? não — ver regra de secrets do brief e `docs/ARQUITETURA.md`).
- Mesma licença (`CC BY 4.0`) e mesma atribuição de fonte do dataset de origem.

---

## 6. Nota LGPD

> **Regra dura:** o portal público expõe **exclusivamente dados agregados**. Microdados com
> identificação direta ou indireta de pessoa física/jurídica **não** são publicados.

- **Nunca publicar** CPF, CNPJ, NIT/CAF individual, nome de produtor(a), inscrição estadual,
  coordenada de imóvel individual ou qualquer campo que identifique pessoa natural/jurídica.
- **Agregação mínima:** publicar somente em recortes que impeçam reidentificação. Aplicar
  **supressão de célula** (n pequeno) quando a contagem de unidades por célula for baixa o
  suficiente para reidentificar — registrar a supressão em `notas` do dataset.
- **Bases sensíveis explícitas:** a base **Compra Direta & Leite das Crianças**
  (eixo `credito-politicas`, status `interno` em `eixos.json`, "cruza CPF/CNPJ") só entra no
  portal como **agregado** (por município/regional/ano/programa) — jamais o microdado.
- **ETL responsável:** a anonimização/agregação ocorre no ETL, antes de qualquer arquivo
  chegar a `assets/data/`. O repositório público **não** deve conter microdado pessoal em
  histórico Git (se entrar por engano, é incidente: limpar histórico + rotacionar acessos).
- **Atribuição ≠ exposição:** declarar `fonte`/`orgao` (instituição) é obrigatório; identificar
  indivíduos é proibido. Em caso de dúvida sobre reidentificação, **não publicar** e escalar.

---

## 7. Checklist de publicação por painel

Antes de marcar um dataset como publicado:

- [ ] Arquivo **CSV** UTF-8 (sem BOM, `,`/`.`) gerado pelo ETL versionado.
- [ ] Espelho **JSON** (e XLSX se aplicável) gerados a partir do CSV.
- [ ] **Dicionário** `{dataset}.dict.json` completo (toda coluna documentada).
- [ ] `cod_ibge` presente (granularidade municipal) e `regional_idr` derivável via `geo/municipios_ref_idr.csv`.
- [ ] Entrada no **`catalog.json`** com todos os campos obrigatórios e `eixo` válido em `eixos.json`.
- [ ] **Licença** declarada (padrão CC BY 4.0) e **fonte/órgão** atribuídos.
- [ ] **Versão** e `ultima_atualizacao` corretos; bump de MAJOR se o esquema mudou.
- [ ] **LGPD** verificada: só agregados, sem CPF/CNPJ, supressão de células pequenas registrada.
- [ ] `catalog.json` valida contra `catalog.schema.json` no CI.
- [ ] Botão "Baixar dados" + link de dicionário acessíveis no painel (WCAG AA: teclado, foco visível, `alt`/rótulos).
- [ ] (Opcional) Espelhado no CKAN `dados.pr.gov.br` se houver convênio.
