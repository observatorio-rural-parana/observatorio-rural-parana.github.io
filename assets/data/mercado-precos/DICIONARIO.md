# Dicionário de Dados — Preços diários (SIMA) e séries de preços

> Eixo **`mercado-precos`** (ver `assets/data/eixos.json`). Painel primário:
> **Preços diários (SIMA)** — `avnergomes/precos-diarios`
> (<https://avnergomes.github.io/precos-diarios/>, com API Flask/Render).
>
> Fonte da verdade de publicação: `docs/DADOS-ABERTOS.md`. Geografia e chave única:
> `docs/GEO.md`. Idioma: **pt-BR**. Atribuição de fonte sempre explícita.
>
> **Origem dos dados:** SIMA/SEAB — Sistema de Informação de Mercado Agrícola da
> Secretaria da Agricultura e do Abastecimento do Paraná (SEAB · IDR-Paraná),
> coletado de `celepar7.pr.gov.br` (resumos diários `ResumoSIMA_*.xls`).
> Cobertura temporal observada **2001–2026** (o README do painel cita 2003–2026;
> os arquivos consolidados começam em 2001-08). Atualização **diária** via
> GitHub Actions; ~22 praças/regiões → padronizadas para os **23 núcleos
> regionais do IDR-Paraná**; ~22 produtos monitorados.

---

## 1. Proveniência e chave geográfica `regional_idr`

A granularidade nativa do SIMA é por **praça/região de coleta**. O ETL do painel
(`api/etl_regional.py`) normaliza essas praças para os **23 núcleos regionais do
IDR-Paraná** por **nome** (campo `regional` no CSV; `r` no JSON), usando uma tabela
de aliases (abreviações históricas das planilhas → nome padrão). A lista padrão
declarada no ETL é exatamente:

`Apucarana, Campo Mourão, Cascavel, Cianorte, Cornélio Procópio, Curitiba, Dois Vizinhos,
Francisco Beltrão, Guarapuava, Irati, Ivaiporã, Laranjeiras do Sul, Londrina, Maringá,
Paranaguá, Paranavaí, Pato Branco, Pitanga, Ponta Grossa, Santo Antônio da Platina,
Toledo, Umuarama, União da Vitória`.

> **Observação (real, não invento):** os JSONs publicados também contêm o rótulo
> **`Jacarezinho`** como regional com dados — variação histórica de praça que mapeia
> ao núcleo **Santo Antônio da Platina** (mesma macrorregião Norte Pioneiro). Tratar
> no de-para; não é um 24º núcleo.

**Vínculo com a chave canônica `regional_idr` (ver `docs/GEO.md`):**

- A chave de junção oficial do observatório é **`regional_idr` = `creg_idr`**
  (código do núcleo, string com zero à esquerda, `01`–`23`, sem `08`).
- O dado-fonte traz o **nome** do núcleo (`regional`), que corresponde a **`reg_idr`**
  (rótulo) no de-para canônico `assets/data/geo/municipios_ref_idr.csv`.
- Portanto, no ETL de ingestão para o portal, **derivar `regional_idr` (código) a
  partir do nome `regional`** via join por `reg_idr` no de-para — **nunca** casar por
  nome em runtime de visualização (acento/grafia divergem entre fontes). A coluna
  `regional_idr` (código) é **adicionada na ingestão** e não existe no dado-fonte bruto.
- Este painel **não** tem granularidade municipal: não há `cod_ibge` no dado-fonte.
  A agregação municipal → regional **não se aplica** aqui; o dado já nasce por região.

---

## 2. Dataset canônico — registro diário por regional

Arquivo-fonte primário no repo do painel:
`data/processed/consolidated_regional.csv` (≈ 78 MB; uma linha por
data × produto × regional). Cabeçalho **real** (com BOM UTF-8):
`data,ano,mes,dia,produto,unidade,categoria,regional,preco,arquivo`.

Espelho web do mesmo grão (lista de objetos abreviados):
`dashboard/public/data/detailed_regional.json` → `{ "records": [ {d,a,m,p,c,r,u,v} ] }`.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `data` | `data` | — (ISO `AAAA-MM-DD`) | Data da cotação diária. | `2001-08-01` … presente. JSON: campo `d`. | SIMA/SEAB | Dias úteis com coleta; nem todo produto cotado todo dia. |
| `ano` | `ano` | ano (`AAAA`) | Ano de referência (derivado de `data`). | `2001`–`2026`. JSON: campo `a`. | SIMA/SEAB (derivado no ETL) | Redundante com `data`; mantido para filtros/agregação. |
| `mes` | `inteiro` | mês (1–12) | Mês de referência (derivado de `data`). | `1`–`12`. JSON: campo `m`. | SIMA/SEAB (derivado no ETL) | — |
| `dia` | `inteiro` | dia (1–31) | Dia do mês (derivado de `data`). | `1`–`31`. | SIMA/SEAB (derivado no ETL) | Não exportado no espelho JSON `detailed_regional.json`. |
| `produto` | `texto` | — | Produto agropecuário cotado (nomenclatura SIMA padronizada pelo ETL). | ~22 produtos; ex.: `Soja industrial tipo 1`, `Milho amarelo tipo 1`, `Boi em pé`, `Vaca em pé`, `Suíno vivo`, `Frango de corte`, `Trigo pão`, `Feijão preto tipo 1`, `Feijão carioca tipo 1`, `Arroz em casca tipo 1`, `Café em coco`, `Café beneficiado`, `Algodão em caroço`, `Erva-mate folha em barranco`, `Mandioca industrial`. JSON: campo `p`. | SIMA/SEAB | Domínio padronizado por regras de regex no ETL (`api/etl_regional.py`). |
| `unidade` | `texto` | — | Unidade física da cotação do produto. | Ex.: `sc 60 Kg`, `arroba`, `kg`, `kg renda`. JSON: campo `u`. | SIMA/SEAB | Preço **é por unidade** (não por kg uniforme); comparar entre produtos exige normalizar. |
| `categoria` | `texto` | — | Categoria/grupo do produto (classificação do ETL). | `Grãos`, `Pecuária`, `Café`, `Florestal`, `Mandioca` (no consolidado regional); o ETL também prevê `Frutas`, `Hortaliças`. JSON: campo `c`. | SIMA/SEAB (classificado no ETL) | Mapeamento produto→categoria definido em `CATEGORIAS` no ETL. |
| `regional` | `texto` | — | Núcleo regional IDR (nome/sede) onde a cotação foi coletada. | 23 núcleos IDR (lista em §1) + rótulo histórico `Jacarezinho`. JSON: campo `r`. | SIMA/SEAB → padronizado a núcleo IDR no ETL | **Rótulo** = `reg_idr`. Derivar `regional_idr` (código `creg_idr`) por join com `geo/municipios_ref_idr.csv`. **Não** casar por nome em runtime. |
| `regional_idr` | `codigo` | — | **(inferido / a derivar na ingestão)** Código do núcleo regional IDR — chave canônica de junção do observatório. | `01`–`23` (string c/ zero à esquerda; sem `08`); FK → `geo/municipios_ref_idr.csv` (`creg_idr`). | IDR-Paraná (derivado no ETL do hub) | **Não existe no dado-fonte**; adicionado na ingestão a partir de `regional` (`reg_idr`). Ver §1 e `docs/GEO.md`. |
| `preco` | `decimal` | R$/unidade | Preço cotado no dia/produto/regional, em reais correntes por `unidade`. | ≥ 0; valores observados de ~`0,8` a milhares (café beneficiado). JSON: campo `v`. | SIMA/SEAB | Reais **correntes** (não deflacionado). Decimal com ponto. Há ruído/outliers históricos em registros antigos. |
| `arquivo` | `texto` | — | Nome do arquivo-fonte bruto de origem da linha (rastreabilidade). | Ex.: `ResumoSIMA_Ago01.xls`. | SIMA/SEAB | Proveniência por linha; não é dado analítico. Pode vir vazio em linhas agregadas. |

> **Chave primária lógica:** `(data, produto, regional)`. `regional_idr` (código) é a
> chave de **agregação/junção** territorial após a derivação.

---

## 3. Dataset agregado estadual — registro diário (sem regional)

Arquivo: `data/processed/consolidated.csv` (≈ 5,6 MB). Cabeçalho **real**:
`data,ano,mes,dia,produto,unidade,categoria,preco_medio,preco_minimo,preco_maximo,num_cotacoes,arquivo`.
Espelho web: `dashboard/public/data/detailed.json` → `{records:[{d,a,p,c,u,pm}]}`
(neste espelho o preço médio é o campo **`pm`**).

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `data` | `data` | ISO `AAAA-MM-DD` | Data da cotação. | `2001-08`… JSON: `d`. | SIMA/SEAB | — |
| `ano` | `ano` | `AAAA` | Ano (derivado). | `2001`–`2026`. JSON: `a`. | SIMA/SEAB (derivado) | — |
| `mes` | `inteiro` | 1–12 | Mês (derivado). | `1`–`12`. | SIMA/SEAB (derivado) | Ausente no espelho `detailed.json`. |
| `dia` | `inteiro` | 1–31 | Dia (derivado). | `1`–`31`. | SIMA/SEAB (derivado) | Ausente no espelho `detailed.json`. |
| `produto` | `texto` | — | Produto cotado. | Ver §2. JSON: `p`. | SIMA/SEAB | — |
| `unidade` | `texto` | — | Unidade física. | Ver §2. JSON: `u`. | SIMA/SEAB | — |
| `categoria` | `texto` | — | Categoria do produto. | Ver §2. JSON: `c`. | SIMA/SEAB (classificado) | — |
| `preco_medio` | `decimal` | R$/unidade | Média estadual do preço no dia/produto (entre regionais). | ≥ 0. JSON: campo `pm`. | SIMA/SEAB (agregado no ETL) | Reais correntes. |
| `preco_minimo` | `decimal` | R$/unidade | Mínimo entre regionais no dia/produto. | ≥ 0. | SIMA/SEAB (agregado no ETL) | Não exportado no espelho `detailed.json`. |
| `preco_maximo` | `decimal` | R$/unidade | Máximo entre regionais no dia/produto. | ≥ 0. | SIMA/SEAB (agregado no ETL) | Não exportado no espelho `detailed.json`. |
| `num_cotacoes` | `inteiro` | contagem | Nº de cotações (regionais) que compõem o agregado do dia/produto. | ≥ 1. | SIMA/SEAB (agregado no ETL) | Indicador de cobertura/confiança do agregado. |
| `arquivo` | `texto` | — | Arquivo-fonte bruto de origem. | Ex.: `ResumoSIMA_*.xls`. | SIMA/SEAB | Rastreabilidade; pode ser vazio. |

> Este nível é **estadual** (`cobertura_geografica.nivel = estado`): não carrega
> `regional` nem `regional_idr`.

---

## 4. Espelhos derivados (JSON) consumidos pelo dashboard

Gerados a partir dos consolidados (`api/preprocess_data.py` / `etl_regional.py`).
São **agregações** para visualização; documentados aqui por transparência. A chave
geográfica, quando presente, é o **nome do núcleo** (`reg_idr`) — derivar
`regional_idr` por join com o de-para.

| arquivo (`dashboard/public/data/…`) | estrutura-chave (campos reais) | grão | observações |
|---|---|---|---|
| `aggregated.json` | `metadata{generated_at,total_records,year_min,year_max}`, `by_year{ano:{media,registros}}`, `by_category{categoria:{media,registros}}`, `by_product{produto:{media,categoria}}` | estado | Totais e médias correntes. |
| `daily_series.json` | `products{produto:[{d,p}]}` | estado/produto | `d`=data, `p`=preço diário (série). |
| `timeseries.json` | `by_period{"AAAA-MM":{media,count}}` | estado/mês | Série mensal estadual agregada. |
| `regional_prices.json` | `by_regional{regional:{total_records,avg_price,products,year_min,year_max}}` | regional | `regional` = nome do núcleo (`reg_idr`). |
| `regional_timeseries.json` | `by_regional{regional:{"AAAA-MM":{mean,count}}}` | regional/mês | — |
| `regional_statistics.json` | `stats{regional:{total_records,total_products,total_categories,year_range,price_stats{mean,median,std,min,max},top_products{},categories{}}}` | regional | — |
| `regional_comparison.json` | `comparisons{produto:{regions{regional:{mean,min,max,std,count}},spread,spread_pct,cheapest,most_expensive}}` | produto×regional | Comparação interregional de preço. |
| `regional_spread.json` | `by_product{produto:{"AAAA-MM":{spread_pct,min,max,mean}}}` | produto/mês | Dispersão de preço entre regionais. |
| `volatility.json` | `by_product{produto:{"AAAA-MM":{std,cv,range_pct,n}}}` | produto/mês | `cv`=coef. variação (%); `n`=nº cotações. |
| `regional_filters.json` | `regionais[]`, `regionais_com_dados[]`, `regional_products{regional:[produto]}` | catálogo | Domínios para a UI. |
| `filters.json` | `category_products{categoria:[produto]}` | catálogo | Domínios para a UI. |
| `forecast_products.json` | `{gerado_em,total,produtos:[{produto,slug,modelos[]}]}` | catálogo | Previsões ML: `modelos` ∈ `linear,arima,auto_arima,random_forest,xgboost`. |
| `forecasts/` (dir) | um arquivo por produto (previsões) | produto | **(inferido)** séries previstas geradas por `scripts/generate_forecasts.py`. |

> **Previsões (ML):** valores de `forecasts/*` e `forecast_products.json` **não são
> dados observados do SIMA** — são estimativas de modelo. Rotular explicitamente como
> "previsão (modelo)" na UI e no catálogo; nunca misturar com a série histórica
> oficial sem distinção visual.

---

## 5. Domínios de referência

- **Produtos** (campo `produto`/`p`) e **categorias** (`categoria`/`c`): domínios
  reais publicados em `filters.json` (`category_products`) e `regional_filters.json`
  (`regional_products`). Categorias observadas no consolidado regional:
  `Grãos`, `Pecuária`, `Café`, `Florestal`, `Mandioca`.
- **Unidades** (`unidade`/`u`): `sc 60 Kg`, `arroba`, `kg`, `kg renda` (conforme
  produto; ver `PRODUCT_UNITS` no ETL).
- **Regionais** (`regional`/`r`): 23 núcleos IDR (lista em §1) — chave canônica
  `regional_idr` (`creg_idr`) derivada por `reg_idr` no de-para `geo/municipios_ref_idr.csv`.

---

## 6. Notas de carga, qualidade e conformidade

- **Reais correntes:** todos os preços são nominais; para séries comparáveis,
  deflacionar **fora** do dataset (deflator não embutido) — mesma diretriz do VBP.
- **Preço por unidade heterogênea:** `preco` é por `unidade` do produto (sc, arroba,
  kg, kg renda); não comparar produtos sem normalizar a unidade.
- **BOM no CSV-fonte:** `consolidated*.csv` do repo de origem trazem **BOM UTF-8**.
  Ao publicar no portal (P2 de `docs/DADOS-ABERTOS.md`), **regerar CSV UTF-8 sem BOM**,
  separador `,`, decimal `.`.
- **Chave geográfica:** o dado-fonte usa **nome** de regional; a coluna canônica
  `regional_idr` (código) deve ser **derivada na ingestão** (ver §1). Sem `cod_ibge`
  (não há grão municipal neste painel).
- **Rótulo `Jacarezinho`:** mapear para o núcleo IDR correspondente no de-para; não é
  um 24º núcleo.
- **Cobertura temporal:** README do painel cita **2003–2026**; os consolidados começam
  em **2001-08**. Adotar a cobertura **real dos arquivos (2001–2026)** e registrar a
  discrepância. Lacunas/contagens baixas existem em anos antigos (ver `num_cotacoes`).
- **Previsões ≠ observações:** ver §4 (separar série ML da série SIMA).
- **LGPD:** dados são **agregados de mercado por região/produto/dia** — não contêm
  pessoa física/jurídica. Conforme §6 de `docs/DADOS-ABERTOS.md` (só agregados).
- **Licença:** o **código** do repositório `precos-diarios` está sob **MIT**
  (© 2024–2026 Avner Gomes). A **licença dos dados** segue o padrão do portal
  **CC BY 4.0 (a confirmar)**, preservando atribuição à fonte primária **SIMA/SEAB
  (SEAB · IDR-Paraná)**. Confirmar com a SEAB os termos de uso/redistribuição do SIMA.

---

## 7. Datasets irmãos do eixo `mercado-precos`

Mesmo eixo, fonte SEAB/IDR-Paraná; catalogar separadamente com seus próprios
dicionários. Ambos têm granularidade regional (≈22 regiões) → derivar `regional_idr`.

- **`precos-florestais`** — `avnergomes/precos-florestais`
  (<https://avnergomes.github.io/precos-florestais/>). Preços de **produtos florestais**
  (madeira, papel/celulose, resinas, erva-mate etc.). **Período 1997–2025**; **10
  categorias, 96 produtos, 22 regiões**. Fonte **SEAB/IDR-Paraná** (compilações XLS/XLSX
  anuais em `/data/`). Inclui previsões e mapa regional.
- **`precos-de-terras`** — `avnergomes/precos-de-terras`
  (<https://avnergomes.github.io/precos-de-terras/>). Preços de **terras rurais** por
  região e **categoria de terra**. **Período 1998–2025**. Fonte **SIPT/SEAB**
  (Sistema de Informação de Preços de Terras) — origem em **PDF** extraído por
  `extract_pdfs.py`/`parse_pdfs.py`; aplicação de busca Flask (`price_search/`).
  Inclui mapa coroplético municipal.

---

### Referências internas
- `docs/DADOS-ABERTOS.md` — esquema de catálogo/dicionário, formatos, licença, LGPD.
- `docs/GEO.md` — chave `regional_idr`, de-para `municipios_ref_idr.csv` (`reg_idr`/`creg_idr`).
- `assets/data/eixos.json` — eixo `mercado-precos` (fontes: DERAL/SIMA, CEASA-PR, DEFLOP, SIPT).
- Repo-fonte: `avnergomes/precos-diarios` — README, `api/etl_regional.py`, `data/processed/consolidated_regional.csv`.
