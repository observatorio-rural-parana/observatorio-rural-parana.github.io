# Cookiecutter de Painel — Observatório Rural Paranaense

> Template padrão (esqueleto) de um **painel temático** do Observatório Rural
> Paranaense. Todo painel do ecossistema (ver `assets/data/eixos.json`) segue
> esta mesma arquitetura: um **pipeline** Python que produz **dados abertos**
> estáticos e um **front** React que os consome, publicado em **GitHub Pages**.
>
> Fontes da verdade (NÃO duplicar/divergir — leia antes de codar):
> - `docs/PROJETO-BRIEF.md` — decisões travadas, convenções de autoria.
> - `docs/DADOS-ABERTOS.md` — contrato de dados abertos e esquema do `catalog.json`.
> - `docs/GEO.md` — chave geográfica `regional_idr` e de-para canônico.
> - `assets/css/tokens.css` — design system (cores/tipografia; sempre `var(--…)`).
> - `assets/data/eixos.json` — taxonomia de eixos/painéis (FK do campo `eixo`).
>
> Idioma de conteúdo: **pt-BR**. Atribuição de fonte sempre explícita.
> LGPD: portal público expõe **somente agregados** — nunca CPF/CNPJ.

---

## 1. Para que serve

Padronizar como cada painel temático é construído, de ponta a ponta, para que:

- todos consumam o **mesmo design system** (`tokens.css`) e a **mesma chave
  geográfica** (`regional_idr`);
- todos **entreguem o dado** (download + dicionário + catálogo), não só a
  visualização — o diferencial declarado no brief (decisão travada nº 4);
- a publicação seja **reprodutível** (ETL versionado) e **estática** (sem backend
  em runtime, conforme `docs/GEO.md`).

Este diretório é um **esqueleto**: copie-o para o repo do painel, renomeie os
marcadores `{eixo}`/`{dataset}` e preencha a regra de negócio. Os arquivos Python
trazem comentários `TODO:` onde a lógica específica do painel deve entrar.

---

## 2. Como usar o template

1. **Escolha o eixo** em `assets/data/eixos.json` (campo `eixos[].id`). Ex.:
   `desempenho-economico`, `mercado-precos`, `comercio-exterior`,
   `credito-politicas`, `ater`. O `id` do eixo **não** se inventa: tem que existir
   na taxonomia.
2. **Copie** `templates/painel/` para o repositório do painel (ou para uma pasta
   de trabalho), preservando a estrutura.
3. **Defina** o(s) `{dataset}` em **kebab-case**, estável e descritivo
   (ex.: `vbp-municipios`, `precos-sima-diarios`). Cada dataset vira o `id` de
   catálogo prefixado pelo eixo: `{eixo}/{dataset}`.
4. **Implemente o pipeline** na ordem (cada etapa abaixo é um arquivo em
   `pipeline/`):

   ```
   ingest  →  model  →  export_open_data  →  (report)
   ```

   - `pipeline/ingest.py` — baixa/lê a fonte bruta. **Sem regra de negócio.**
   - `pipeline/model.py` — transformação, joins, normalização para `regional_idr`
     usando `assets/data/geo/municipios_ref_idr.csv`. **Aqui mora a regra de negócio.**
   - `pipeline/export_open_data.py` — escreve `{dataset}.csv` + `{dataset}.json`,
     gera/atualiza o `DICIONARIO.md`/`{dataset}.dict.json` e a entrada no
     `catalog.json`. **Só agregados; nunca CPF/CNPJ.**
   - `report` (opcional) — relatórios/figuras derivados; não faz parte do contrato
     de dados abertos.
5. **Preencha o dicionário** a partir de `DICIONARIO.template.md`, com base nas
   colunas **reais** do dataset (marque campos inferidos como `(inferido)`).
6. **Registre no catálogo** copiando `catalog-entry.template.json` e anexando a
   entrada ao `assets/data/catalog.json` do hub.
7. **Construa o front** (seção 5) consumindo os tokens e os dados abertos gerados.
8. **Rode o checklist** de `docs/DADOS-ABERTOS.md` §7 antes de publicar.

> Os scripts são **idempotentes**: rodar duas vezes com a mesma fonte produz o
> mesmo resultado (mesmos arquivos, catálogo atualizado in-place pelo `id`).

---

## 3. Arquitetura padrão

### 3.1 Pipeline (ETL Python → arquivos estáticos)

```
                    fonte bruta (API, CSV, XLSX, planilha SEAB/IDR…)
                              │
            ┌─────────────────▼─────────────────┐
            │  ingest.py                          │  baixa/lê o bruto e o
            │  (sem regra de negócio)             │  materializa em data/raw/
            └─────────────────┬─────────────────┘
                              │  DataFrame/arquivo bruto
            ┌─────────────────▼─────────────────┐
            │  model.py                           │  regra de negócio:
            │  transform + join + normaliza p/    │  limpa, agrega, deriva
            │  regional_idr (via de-para canônico)│  regional_idr, valida LGPD
            └─────────────────┬─────────────────┘
                              │  DataFrame "tidy" (agregado)
            ┌─────────────────▼─────────────────┐
            │  export_open_data.py                │  CONTRATO DE DADOS ABERTOS:
            │  {dataset}.csv + {dataset}.json     │  escreve dados, dicionário e
            │  + DICIONARIO.md/.dict.json         │  atualiza catalog.json
            │  + entrada no catalog.json          │  (idempotente por id)
            └─────────────────┬─────────────────┘
                              │
                       (report.py, opcional)        figuras/relatórios derivados
```

Princípios (de `docs/GEO.md` e `docs/DADOS-ABERTOS.md`):

- **Estático, sem backend em runtime.** O ETL roda na ingestão/atualização; o
  front só faz `fetch()` de arquivos.
- **Dependências sóbrias.** `pandas` é suficiente para os esqueletos; evitar
  dependências exóticas. Manter funções pequenas e arquivos focados.
- **Boundary validation.** Validar a fonte na ingestão e o resultado na
  exportação; falhar rápido com mensagem clara.

### 3.2 Front (React 18 + Vite + Tailwind + Recharts/Leaflet)

> Observação de coerência: o **hub** (`observatorio-rural-parana.github.io`) é
> HTML/CSS/JS **vanilla** (ver `PROJETO-BRIEF.md`). Os **painéis temáticos** do
> ecossistema usam a stack React 18 + Vite + Tailwind + Recharts/Leaflet (família
> `avnergomes`). Ambos consomem os **mesmos tokens** e a **mesma chave geográfica**.

- **React 18 + Vite** — SPA estática, build para GitHub Pages.
- **Tailwind** — utilitários de layout; **as cores/tipografia vêm dos tokens do
  observatório** (`assets/css/tokens.css`), nunca hex solto. Mapeie os tokens no
  `tailwind.config.js` para `var(--…)`:

  ```js
  // tailwind.config.js (esqueleto)
  export default {
    content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
    theme: {
      extend: {
        colors: {
          paper:  "var(--paper)",
          ink:    "var(--ink)",
          brand:  "var(--green)",   // marca primária IDR
          azul:   "var(--azul)",    // institucional Gov-PR
          olive:  "var(--olive)",
          amber:  "var(--amber)",
          clay:   "var(--clay)",
        },
        fontFamily: {
          serif: "var(--serif)",
          sans:  "var(--sans)",
          mono:  "var(--mono)",
        },
        maxWidth: { content: "var(--maxw)" },
      },
    },
  };
  ```

  Importe os tokens uma vez (ex.: do hub publicado ou de uma cópia versionada):

  ```css
  /* src/index.css — antes do Tailwind */
  @import url("https://observatorio-rural-parana.github.io/assets/css/tokens.css");
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```

- **Recharts** — gráficos (séries temporais, barras, composição). Cores das
  séries via tokens (`--green`, `--olive`, `--azul`, `--amber`, `--clay`).
- **Leaflet** (ou SVG/`topojson-client`) — mapas. Choropleth por
  `regional_idr`/`cod_ibge`, **junção sempre por chave, nunca por nome** (ver
  `docs/GEO.md` §4). Para choropleth simples por 23 núcleos, o SVG de
  `assets/data/geo/pr_nucleos_regionais.json` dispensa lib de mapa.
- **Consumo dos dados abertos.** O front lê os mesmos `{dataset}.csv`/`.json`
  publicados pelo pipeline (a visualização e o download apontam para a **mesma**
  fonte). Botão "Baixar dados" + link de dicionário sempre visíveis e acessíveis
  (WCAG AA: teclado, foco visível via `--focus-ring`, `alt`/rótulos).

### 3.3 Deploy (GitHub Pages)

- Build estático do front (`vite build`) publicado em GitHub Pages (Actions ou
  branch `gh-pages`). Incluir `.nojekyll`.
- Os **dados abertos** vivem sob `assets/data/{eixo}/` **no hub**
  (fonte canônica única); o front do painel consome por **URL estável** do hub.
- **Não duplicar** malhas geográficas por painel — reusar a cópia única do hub
  (`assets/data/geo/`), conforme `docs/GEO.md` §4.

---

## 4. Contrato de Dados Abertos (o que todo painel emite)

> Resumo acionável de `docs/DADOS-ABERTOS.md`. Em caso de divergência, **o doc
> manda**.

Para **cada dataset**, o painel emite obrigatoriamente:

| Artefato | Caminho | Papel |
|----------|---------|-------|
| `{dataset}.csv` | `assets/data/{eixo}/{dataset}.csv` | Formato **canônico** — CSV UTF-8 **sem BOM**, separador `,`, decimal `.`. |
| `{dataset}.json` | `assets/data/{eixo}/{dataset}.json` | Espelho para consumo programático/web (gerado a partir do CSV). |
| **DICIONÁRIO** | `assets/data/{eixo}/{dataset}.dict.json` (máquina) + `DICIONARIO.md` (humano) | Toda coluna documentada: `coluna \| tipo \| unidade \| descrição \| domínio \| fonte \| notas`. |
| **Entrada no catálogo** | uma entrada em `assets/data/catalog.json` | Manifesto único do portal, lido por máquina (ver campos abaixo). |
| `{dataset}.xlsx` | `assets/data/{eixo}/{dataset}.xlsx` | **Opcional** — conveniência de gestores; gerado do CSV, nunca a fonte primária. |

**Regras duras do contrato:**

- **`regional_idr` sempre presente como chave.** Datasets municipais carregam
  `cod_ibge` (chave forte) e **devem** poder derivar `regional_idr` via join com
  `assets/data/geo/municipios_ref_idr.csv`. Datasets já regionais usam
  `regional_idr` (`creg_idr`, string com zero à esquerda) diretamente.
- **Junção por chave, nunca por nome.** Acento/grafia/caixa divergem entre fontes.
- **Não duplicar o de-para** dentro dos datasets de domínio — derivar no ETL.
- **Só agregados.** Nunca CPF, CNPJ, NIT/CAF individual, nome de produtor,
  coordenada de imóvel individual. Aplicar **supressão de célula** quando o n for
  pequeno o bastante para reidentificar e registrar em `notas`.
- **Atribuição.** Todo dataset declara `fonte` (origem primária) e `orgao`
  (instituição). Nunca dado "órfão".
- **Versionamento.** `versao` SemVer reduzido `MAJOR.MINOR` (MAJOR = mudança de
  esquema; MINOR = nova carga) + `ultima_atualizacao` ISO `AAAA-MM-DD`.

### 4.1 Campos da entrada no `catalog.json` (obrigatórios salvo indicado)

Conforme `docs/DADOS-ABERTOS.md` §2.2:

| Campo | Tipo | Obrig. | Observação |
|-------|------|:------:|-----------|
| `id` | string | sim | `{eixo}/{dataset}` (kebab-case, imutável). |
| `titulo` | string | sim | Título legível pt-BR. |
| `eixo` | string | sim | FK → `eixos.json` (`eixos[].id`). |
| `descricao` | string | sim | 1–3 frases. |
| `fonte` | string | sim | Origem primária do dado. |
| `orgao` | string | sim | Instituição responsável. |
| `periodicidade` | string | sim | `anual`\|`mensal`\|`diaria`\|`semanal`\|`eventual`\|`unica`. |
| `ultima_atualizacao` | date | sim | ISO `AAAA-MM-DD`. |
| `cobertura_temporal` | objeto | sim | `{ "inicio", "fim" }`. |
| `cobertura_geografica` | objeto | sim | `{ "nivel", "unidades" }`; `nivel` ∈ `estado`\|`mesorregiao`\|`regional_idr`\|`municipio`. |
| `formatos` | array | sim | Subconjunto de `["csv","json","xlsx"]`; `csv` sempre presente. |
| `arquivos` | array | sim | `{ "formato","url","bytes","sha256" }`; `url` relativa à raiz. |
| `licenca` | objeto | sim | Padrão CC BY 4.0 (`id`,`nome`,`url`). |
| `dicionario` | url | sim | URL do `*.dict.json`. |
| `versao` | string | sim | `MAJOR.MINOR`. |
| `painel` | objeto | não | `{ "nome","url" }`. |
| `notas` | string | não | Limitações, ressalvas LGPD/supressão. |

O `export_open_data.py` preenche `bytes`/`sha256` automaticamente e faz **upsert**
da entrada por `id` (idempotente). Validar o `catalog.json` contra
`catalog.schema.json` no CI antes de publicar.

---

## 5. Estrutura de arquivos do template

```
templates/painel/
├── README.md                       ← este arquivo
├── DICIONARIO.template.md          ← modelo de dicionário (humano)
├── catalog-entry.template.json     ← modelo de uma entrada de catálogo
└── pipeline/
    ├── ingest.py                   ← ingestão (sem regra de negócio)
    ├── model.py                    ← regra de negócio + normalização regional_idr
    └── export_open_data.py         ← emite CSV/JSON + dicionário + catálogo
```

---

## 6. Checklist (resumo de `docs/DADOS-ABERTOS.md` §7)

- [ ] `{dataset}.csv` UTF-8 sem BOM (`,`/`.`) gerado pelo ETL versionado.
- [ ] `{dataset}.json` (e `.xlsx` se aplicável) gerados a partir do CSV.
- [ ] `{dataset}.dict.json` + `DICIONARIO.md` completos (toda coluna documentada).
- [ ] `cod_ibge` presente (se municipal) e `regional_idr` derivável via de-para.
- [ ] Entrada no `catalog.json` com todos os campos obrigatórios e `eixo` válido.
- [ ] Licença (CC BY 4.0) e fonte/órgão atribuídos.
- [ ] `versao` e `ultima_atualizacao` corretos; bump de MAJOR se o esquema mudou.
- [ ] LGPD: só agregados, sem CPF/CNPJ; supressão de células pequenas registrada.
- [ ] `catalog.json` valida no CI; botão "Baixar dados" + dicionário acessíveis (WCAG AA).
