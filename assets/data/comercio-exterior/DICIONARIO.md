# Dicionário de dados — Comércio exterior do agronegócio paranaense

> Dataset do eixo **`comercio-exterior`** (ver `assets/data/eixos.json`). Painel-fonte:
> **ComexStat Paraná (2020–2025)** — repositório `avnergomes/comexstat-parana`
> (<https://avnergomes.github.io/comexstat-parana/>).
>
> **Fonte primária:** ComexStat / MDIC (Ministério do Desenvolvimento, Indústria,
> Comércio e Serviços) — Secretaria de Comércio Exterior (SECEX). Recorte agro
> (capítulos NCM/SH 01–24 + cap. 31 fertilizantes + posição SH4 3808 defensivos),
> filtro UF = `PR`, período **2020–2025**.
>
> **Chave geográfica canônica do observatório:** `regional_idr` (399 municípios →
> 23 regionais IDR → 7 mesorregiões). Ver `docs/GEO.md` e o de-para canônico
> `assets/data/geo/municipios_ref_idr.csv`. **Importante:** o ComexStat publica o
> fluxo municipal pela coluna de código de município `CO_MUN`, que **é o código
> IBGE de 7 dígitos** (ex.: `4118204` = Paranaguá, `4106902` = Curitiba). Logo
> `regional_idr` é **derivável** via *join* `cod_ibge` (= `CO_MUN`) →
> `geo/municipios_ref_idr.csv`. Nas séries por país, produto e cadeia (sem recorte
> municipal) o nível geográfico é o **estado** (`PR`).
>
> **Convenções (não divergir):** conteúdo pt-BR; formato canônico CSV (UTF-8 sem BOM,
> separador `,`, decimal `.`); espelho JSON para consumo web. Os arquivos publicados
> hoje no painel-fonte são **JSON agregados** (`dashboard/public/data/*.json`); o
> CSV/JSON canônico do portal será derivado deles no ETL (ver §4 de
> `docs/DADOS-ABERTOS.md`). Atribuição de fonte sempre explícita.

---

## 1. Esquema-fonte (colunas reais dos arquivos MDIC por município)

Colunas reais dos arquivos brutos `EXP_{ano}_MUN.csv` / `IMP_{ano}_MUN.csv` do
ComexStat (separador `;`, encoding `latin-1`), conforme `download_municipios.py`
do repositório. São a base de todas as agregações publicadas.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `CO_ANO` | `ano` | ano | Ano de referência da operação de comércio exterior. | `2020`–`2025`. | ComexStat/MDIC (SECEX) | Recorte do painel: 2020–2025. |
| `CO_MES` | `inteiro` | mês | Mês de referência (1–12). | `1`–`12`. | ComexStat/MDIC (SECEX) | Combinado com `CO_ANO` forma o período mensal `AAAA-MM`. |
| `SH4` | `codigo` | — | Código do produto na nomenclatura SH a 4 dígitos (Sistema Harmonizado). | 4 dígitos (zero à esquerda preservado, ex.: `1201`). | ComexStat/MDIC (SECEX) | Os 2 primeiros dígitos formam o capítulo NCM (`CAPITULO`). Recorte agro = caps. 01–24 + 31 + posição 3808. |
| `CO_PAIS` | `codigo` | — | Código SECEX do país parceiro (destino na exportação / origem na importação). | Tabela de países SECEX (`TABELAS_AUXILIARES`, sheet 10). | ComexStat/MDIC (SECEX) | Mapeado para `NO_PAIS` (nome do país). |
| `SG_UF_MUN` | `texto` | — | Sigla da UF do município de origem (exportação) / destino (importação). | `PR` (após filtro do painel). | ComexStat/MDIC (SECEX) | Usado para filtrar o Paraná. |
| `CO_MUN` | `codigo` | — | Código do município (**IBGE 7 dígitos**) de origem/destino da operação. | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | ComexStat/MDIC (SECEX) / IBGE | É o `cod_ibge` do observatório (ex.: `4118204`). `CO_MUN // 100000` = código da UF (41 = PR). Chave para derivar `regional_idr`. |
| `KG_LIQUIDO` | `decimal` | kg | Peso líquido da mercadoria. | ≥ 0. | ComexStat/MDIC (SECEX) | No painel agregado vira o campo `peso`. |
| `VL_FOB` | `decimal` | US$ | Valor FOB (*Free On Board*) da operação, em dólares dos EUA. | ≥ 0. | ComexStat/MDIC (SECEX) | No painel agregado vira o campo `valor`. **Não** convertido para R$ nem deflacionado. |

> Colunas derivadas no ETL a partir do esquema-fonte: `CAPITULO` (= 2 primeiros
> dígitos de `SH4`), `CADEIA` (cadeia produtiva classificada por SH4, ver
> `ncm_cadeias_map.py`), `NO_PAIS` / `NO_MUN` (rótulos via tabelas auxiliares),
> `periodo` (`AAAA-MM`), `saldo` (= exportações − importações), `corrente` (=
> exportações + importações).

---

## 2. Chave geográfica `regional_idr` (obrigatória no portal)

Toda agregação municipal deve carregar `cod_ibge` (= `CO_MUN`) e permitir derivar
`regional_idr` via *join* com o de-para canônico. Colunas geográficas que o portal
adiciona/exige (derivadas no ETL, **não** duplicar o de-para no dataset):

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `cod_ibge` | `codigo` | — | Código IBGE do município (7 dígitos). É o `CO_MUN` do ComexStat. | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE / ComexStat-MDIC | Chave forte de junção municipal. |
| `municipio` | `texto` | — | Nome oficial do município (acentuação IBGE). | Rótulo controlado pelo de-para geográfico. | IBGE | No painel-fonte vem como `nome` (`NO_MUN`); mantido por legibilidade, **não** usar como chave de join. |
| `regional_idr` | `codigo` | — | Núcleo Regional do IDR-Paraná do município (chave de agregação regional do observatório). | 23 regionais; FK → `geo/municipios_ref_idr.csv` (`creg_idr`), string com zero à esquerda (`"02"`). | IDR-Paraná (de-para) | **(derivado no ETL)** a partir de `cod_ibge` via `geo/municipios_ref_idr.csv`. Não presente no dado bruto do MDIC. |
| `meso_idr` | `texto` | — | Mesorregião IDR a que pertence o município/regional. | 7 mesorregiões IDR (Norte, Metropolitana e Litoral, Oeste, Noroeste, Sudoeste, Centro Sul, Centro). | IDR-Paraná (de-para) | **(derivado no ETL)** via `geo/municipios_ref_idr.csv`. Nível superior de agregação. |

---

## 3. Campos publicados no painel-fonte (arquivos agregados reais)

Estrutura **real** dos arquivos JSON publicados em
`dashboard/public/data/` do repositório `avnergomes/comexstat-parana`. Servem de
base para o CSV/JSON canônico do portal. Salvo indicação, `valor` = `VL_FOB` (US$)
e `peso` = `KG_LIQUIDO` (kg).

### 3.1 `municipios_data.json` — exportações por município (nível municipal → `regional_idr`)

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `codigo` | `codigo` | — | Código IBGE (7 díg.) do município exportador. É o `cod_ibge`. | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | ComexStat/MDIC; IBGE | Ex.: `4118204` (Paranaguá). Chave para derivar `regional_idr`. |
| `nome` | `texto` | — | Nome do município exportador. | Rótulo (`NO_MUN`). | IBGE / ComexStat-MDIC | Rótulo de exibição; não usar como chave. |
| `valor` | `decimal` | US$ | Valor FOB exportado pelo município no período. | ≥ 0; soma 2020–2025. | ComexStat/MDIC (SECEX) | = `VL_FOB`. Em dólares correntes (não deflacionado). |
| `peso` | `decimal` | kg | Peso líquido exportado pelo município no período. | ≥ 0. | ComexStat/MDIC (SECEX) | = `KG_LIQUIDO`. |
| `percentual` | `decimal` | % | Participação do município no total exportado do PR. | 0–100. | DERIVADO (ETL comexstat-parana) | **(inferido — cálculo do painel)** `valor` do município ÷ `totalValor` × 100. |
| `cadeia` | `texto` | — | Cadeia produtiva agregada (presente em `municipiosByCadeia`). | 20 cadeias (ex.: `Sojicultura`, `Avicultura`, `Agroind. Grãos`, `Olericultura`, `Outros`). | DERIVADO (classificação SH4) | Em `municipios_data.json` há também o bloco `municipiosByCadeia` (município × cadeia). |

> Campos de cabeçalho do arquivo: `totalValor` (US$, soma do PR), `totalPeso`
> (kg, soma do PR). O painel publica os **top 50** municípios em `municipios`.

### 3.2 `aggregated.json` — séries e rankings agregados (nível estadual `PR`)

Blocos reais (resumo dos campos por bloco; `exp`/`imp` = exportação/importação):

| bloco | campos reais | unidade | descrição | fonte |
|-------|--------------|---------|-----------|-------|
| `metadata` | `anoMin`, `anoMax`, `anos[]`, `totalExportacoes`, `totalImportacoes`, `produtosExp`, `produtosImp`, `paisesDestino`, `paisesOrigem`, `valorTotalExp`, `valorTotalImp`, `pesoTotalExp` | contagem / US$ / kg | Metadados de cobertura: período, nº de registros, nº de produtos/países, totais FOB e de peso. | ComexStat/MDIC; DERIVADO |
| `filters.capitulos[]` | `codigo`, `nome` | — | Capítulos NCM presentes (ex.: `12` = "Sementes oleaginosas"). | DERIVADO (mapa `CATEGORIAS_NCM`) |
| `filters.cadeias[]` | `nome`, `cor`, `tipo` | — | Cadeias produtivas; `tipo` ∈ `produto`\|`insumo`; `cor` = cor de série do painel-fonte (hex próprio do painel, **não** usar no hub — ver `tokens.css`). | DERIVADO (`ncm_cadeias_map.py`) |
| `filters.paisesExp[]` / `paisesImp[]` | `codigo`, `pais` | — | Países parceiros de exportação/importação. | ComexStat/MDIC |
| `timeseries[]` | `ano`, `valorExp`, `pesoExp`, `produtosExp`, `valorImp`, `pesoImp`, `produtosImp`, `saldo`, `corrente` | US$ / kg / contagem | Série anual estadual; `saldo` = `valorExp` − `valorImp`; `corrente` = `valorExp` + `valorImp`. | ComexStat/MDIC; DERIVADO |
| `timeseriesByCadeia[]` | `ano`, `cadeia`, `valorExp`, `pesoExp`, `valorImp`, `pesoImp` | US$ / kg | Série anual por cadeia produtiva. | DERIVADO |
| `byCategoria.{exportacoes,importacoes}[]` | `categoria`, `valor`, `peso`, `produtos`, `cor` | US$ / kg / contagem | Total por categoria/cadeia. | DERIVADO |
| `byCapitulo.{exportacoes,importacoes}[]` | `CAPITULO_NCM`, `valor`, `peso`, `produtos`, `categoria` | US$ / kg / contagem | Total por capítulo NCM. | DERIVADO |
| `byPais.{exportacoes,importacoes}[]` | `codigo`, `pais`, `valor`, `peso` | US$ / kg | Total por país parceiro (top 50). | ComexStat/MDIC; DERIVADO |
| `byPaisByCadeia.{exportacoes,importacoes}[]` | `codigo`, `pais`, `cadeia`, `valor`, `peso` | US$ / kg | Total por país × cadeia. | DERIVADO |
| `topProdutos.{exportacoes,importacoes}[]` | `ncm`, `descricao`, `CAPITULO_NCM`, `cadeia`, `valor`, `peso`, `capitulo` | US$ / kg | Top 100 produtos (SH4); `ncm` = código SH4; `capitulo` = nome do capítulo. | ComexStat/MDIC; DERIVADO |

### 3.3 `detailed.json` — séries mensais (nível estadual `PR`)

| bloco | campos reais | unidade | descrição | fonte |
|-------|--------------|---------|-----------|-------|
| `exportacoesPorPeriodo[]` | `periodo`, `categoria`, `valor`, `peso` | US$ / kg | Exportação mensal por categoria/capítulo; `periodo` = `AAAA-MM`. | ComexStat/MDIC; DERIVADO |
| `importacoesPorPeriodo[]` | `periodo`, `categoria`, `valor`, `peso` | US$ / kg | Importação mensal por categoria/capítulo. | ComexStat/MDIC; DERIVADO |
| `timeseriesMensal[]` | `periodo`, `valorExp`, `pesoExp`, `valorImp`, `pesoImp`, `saldo` | US$ / kg | Série mensal estadual; `saldo` = `valorExp` − `valorImp`. | DERIVADO |

### 3.4 `map_data.json` — mapa de fluxos por país

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `codigo` | `codigo` | — | Código SECEX do país parceiro. | Tabela de países SECEX. | ComexStat/MDIC | Em `exportacoes[]` e `importacoes[]`. |
| `pais` | `texto` | — | Nome do país parceiro. | Rótulo. | ComexStat/MDIC | 221 destinos / 92 origens. |
| `valor` | `decimal` | US$ | Valor FOB do fluxo com o país no período. | ≥ 0. | ComexStat/MDIC | = `VL_FOB`. |
| `peso` | `decimal` | kg | Peso líquido do fluxo com o país. | ≥ 0. | ComexStat/MDIC | = `KG_LIQUIDO`. |
| `percentual` | `decimal` | % | Participação do país no total do PR. | 0–100. | DERIVADO | **(inferido — cálculo do painel)** `valor` ÷ total × 100. |

### 3.5 `sankey_data.json` — diagrama de cadeias (município → país)

| campo | tipo | descrição | fonte | notas |
|-------|------|-----------|-------|-------|
| `nodes[].id` | `texto` | Identificador do nó (`mun_{nome}` ou `pais_{nome}`). | DERIVADO | Prefixo indica o tipo. |
| `nodes[].name` | `texto` | Rótulo do nó (município ou país). | ComexStat/MDIC | |
| `nodes[].type` | `texto` | Tipo do nó. | DERIVADO | `municipio` \| `pais`. |
| `links[].source` / `target` | `texto` | Nós de origem e destino do fluxo. | DERIVADO | FK → `nodes[].id`. |
| `links[].value` | `decimal` (US$) | Valor FOB do fluxo município→país. | ComexStat/MDIC | = `VL_FOB`. Top 80 fluxos. |
| `linksByCadeia[]` | `source`, `target`, `value`, `cadeia` | Fluxos segmentados por cadeia produtiva. | DERIVADO | |

> **Nota de qualidade (real):** em `sankey_data.json` há rótulo de país com falha de
> codificação UTF-8 (ex.: `pais_\udc8ndia` por "Índia"). Tratar nomes como rótulos e
> juntar por **código**, nunca por nome (regra `docs/GEO.md` §4). Registrar como
> ressalva no `notas` do dataset publicado.

### 3.6 `forecasts.json` — projeção de curto prazo (nível estadual `PR`)

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano da observação ou da projeção. | histórico 2020–2025 + 2 anos projetados. | ComexStat/MDIC; DERIVADO | |
| `valor` | `decimal` | US$ | Valor FOB anual (real para histórico, projetado para previsão). | ≥ 0. | ComexStat/MDIC; DERIVADO | = `VL_FOB`. |
| `valorMin` / `valorMax` | `decimal` | US$ | Limite inferior/superior do intervalo da projeção. | apenas nas linhas `tipo=previsao`. | DERIVADO (modelo) | **(inferido)** IC do modelo (tendência linear / Holt ± 1,96·σ ou ±15% no fallback). |
| `tipo` | `texto` | — | Natureza da linha. | `historico` \| `previsao`. | DERIVADO | Em `exportacoes[]` e `importacoes[]`. |

> Bloco de cabeçalho (quando presente): `modelo` (ex.: `LinearTrend`/`Holt`),
> `geradoEm` (data de geração). Projeções **não são dados oficiais** do MDIC —
> registrar como estimativa metodológica do painel no `notas`.

---

## 4. Notas metodológicas e ressalvas (obrigatórias)

- **Moeda:** todos os valores de `valor` são **`VL_FOB` em US$ correntes** (dólar dos
  EUA), **não** convertidos para reais e **não** deflacionados. Para séries reais,
  deflacionar fora do dataset (deflator não embutido).
- **Recorte agro:** capítulos NCM/SH **01–24** + capítulo **31** (fertilizantes) +
  posição **3808** (defensivos agrícolas), filtro UF = `PR`. Insumos (fertilizantes,
  defensivos) entram como cadeias de **`tipo=insumo`** — distinguir de produtos agro.
- **`regional_idr`:** não vem do MDIC; é **derivada no ETL** por *join* de `cod_ibge`
  (= `CO_MUN`, IBGE 7 díg.) com `geo/municipios_ref_idr.csv`. Tratar `creg_idr` como
  **string com zero à esquerda**. Não há núcleo `08` (lacuna histórica esperada).
- **Nível geográfico por arquivo:** `municipios_data.json` é municipal (→ `regional_idr`);
  os demais agregados (`aggregated`, `detailed`, `map_data`, `sankey`, `forecasts`)
  são **estaduais** (`PR`) ou por país/produto/cadeia, sem desagregação municipal.
- **Cores do painel-fonte:** os campos `cor` (hex) vêm do painel React de origem;
  no hub do observatório usar **sempre** os tokens de `assets/css/tokens.css`
  (`var(--…)`), nunca o hex herdado.
- **LGPD:** dado de comércio exterior agregado por município/país/produto — **sem**
  identificação de pessoa física/jurídica (sem CPF/CNPJ/importador-exportador
  individual). Compatível com publicação pública agregada (ver `docs/DADOS-ABERTOS.md` §6).
- **Licença:** o **código** do repositório de origem é MIT; os **dados** são do
  ComexStat/MDIC (dado público de comércio exterior). O portal adota **CC BY 4.0**
  como licença de publicação **(a confirmar)**, preservando a atribuição ao MDIC/SECEX.

---

## 5. Proveniência

- **Fonte primária:** ComexStat / MDIC — SECEX. Endpoint dos dados municipais:
  `https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/` (`EXP_{ano}_MUN.csv`,
  `IMP_{ano}_MUN.csv`); tabelas auxiliares (países/municípios) do próprio ComexStat.
- **Órgão responsável (publicação no observatório):** IDR-Paraná / SEAB.
- **Painel-fonte:** `avnergomes/comexstat-parana`
  (<https://avnergomes.github.io/comexstat-parana/>); ETL Python (Pandas) →
  JSON estático (`dashboard/public/data/*.json`).
- **Cobertura temporal:** 2020–2025. **Cobertura geográfica:** município / `regional_idr`
  (399 municípios → 23 regionais IDR) e estado (`PR`) nas séries agregadas.
- **Atualização:** workflow automatizado `update-data.yml` (eventual/anual conforme
  cargas do MDIC).
