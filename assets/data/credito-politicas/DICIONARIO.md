# Dicionário de Dados — Crédito Rural e Políticas Públicas

> **Dataset:** `credito-politicas/credito-rural-parana`
> **Painel primário:** Crédito Rural Paraná (SICOR 2013–2026) —
> [`avnergomes/credito-rural-parana`](https://github.com/avnergomes/credito-rural-parana)
> · [painel no ar](https://avnergomes.github.io/credito-rural-parana/)
> **Fonte:** Banco Central do Brasil — SICOR (Sistema de Operações do Crédito Rural
> e do Proagro), API OData pública (`olinda.bcb.gov.br/.../SICOR/.../odata`), filtro
> `nomeUF eq 'PR'`.
> **Órgão responsável:** Banco Central do Brasil (BCB).
> **Cobertura temporal:** 2013–2026 (campo `metadata.anoMin`/`anoMax` do arquivo real).
> **Cobertura geográfica:** município (`codIbge`, 399 municípios) e regional
> (`regional_idr`, derivável). Os endpoints `RegiaoUF*` agregam por região do BCB já
> filtrados para o PR; o nível municipal vem de `MunicipioUF`.
> **Última atualização da carga (no repo):** 2026-02-22 (campo
> `metadata.ultimaAtualizacao`).
> **Idioma:** pt-BR · **Formatos abertos:** CSV (canônico) + JSON (espelho).

---

## 1. Como ler este dicionário

O painel-fonte **não publica um CSV plano único**: publica `dashboard/public/data/aggregated.json`
(≈13,9 MB), um objeto com **várias coleções pré-agregadas** (séries temporais, recortes por
finalidade, programa, produto, município, gênero, Sankey e ranking). Há ainda `forecasts.json`
(projeções de modelos) e `mapeamento_vbp.json` (de-para de nomes de produto).

Para publicação como **dado aberto tabular** no Observatório, cada coleção do `aggregated.json`
deve ser **achatada** pelo ETL em um CSV/JSON irmão (formato canônico CSV UTF-8, separador `,`,
decimal `.`). As seções abaixo documentam as **colunas reais** de cada coleção, na origem, e como
a chave geográfica única **`regional_idr`** entra em cada uma.

> **Convenção geográfica do Observatório (obrigatória — `docs/GEO.md`, `docs/DADOS-ABERTOS.md`):**
> a chave de junção territorial canônica é **`regional_idr`** (399 municípios → 23 regionais →
> 7 mesorregiões). Os dados do SICOR carregam `codIbge` (chave municipal forte); **`regional_idr`
> é derivado no ETL** por *join* com `assets/data/geo/municipios_ref_idr.csv`
> (`codIbge` → `cod_ibge` → `creg_idr`/`reg_idr`/`meso_idr`). **Não duplicar o de-para** dentro
> deste dataset; derivar a partir do arquivo canônico. As coleções já agregadas por "Região do
> BCB" (`RegiaoUF*`) **não** mapeiam 1:1 para a regional IDR — ver §8 (ressalvas).

**Tipos canônicos** (`docs/DADOS-ABERTOS.md` §3): `inteiro`, `decimal`, `texto`, `data`
(`AAAA-MM-DD`), `ano` (`AAAA`), `booleano`, `codigo` (string de código, ex. `cod_ibge`).
Campos marcados **(inferido)** não estão materializados na origem ou tiveram tipo/domínio
deduzido do código de ETL (`scripts/preprocess_data.py`, `scripts/fetch_data.py`); confirmar na
carga antes de publicar.

---

## 2. Chave geográfica `regional_idr` (transversal a todas as coleções municipais)

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `regional_idr` | `codigo` | — | Núcleo Regional do IDR-Paraná do município. **(inferido / derivado)** | 23 regionais; FK → `geo/municipios_ref_idr.csv` (`creg_idr`). String com zero à esquerda (`"02"`); não existe `08`. | IDR-Paraná (de-para) | **Não presente na origem SICOR.** Derivar no ETL: `codIbge` → `cod_ibge` → `creg_idr`. Chave de agregação regional do Observatório. |
| `cod_ibge` | `codigo` | — | Código IBGE do município (7 dígitos). | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE — Malha Municipal | Na origem chama-se `codIbge` (vem de `codMunicIbge`). Tratar como **string** (preservar zeros). |

> A coleção `byMunicipio` (e `bump`, `municipioTotals`) carrega `codIbge`; portanto `regional_idr`
> é derivável para todo recorte municipal. As coleções regionais do BCB (`RegiaoUF*`) usam a
> **região administrativa do próprio BCB**, que **não** equivale à regional IDR — ver §8.

---

## 3. Coleção `byMunicipio` — crédito por município, ano, mês e programa

Granularidade municipal (origem: endpoint `MunicipioUF` do SICOR). É a coleção que sustenta o
mapa coroplético e o cruzamento com `regional_idr`.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano de emissão do contrato (`AnoEmissao`). | `2013`–`2026`. | BCB/SICOR | Convertido para inteiro no ETL. |
| `mes` | `inteiro` | mês | Mês de emissão (`MesEmissao`). | `1`–`12`. | BCB/SICOR | Inteiro 1–12. |
| `codIbge` | `codigo` | — | Código IBGE do município (`codMunicIbge`). | 399 municípios do PR. | BCB/SICOR + IBGE | **String** (preservar zeros). Base da derivação de `regional_idr`. |
| `name` | `texto` | — | Nome do município. | Texto controlado. | IBGE (`ibge_municipios.json`) / SICOR | Resolvido por `ibge_names[codIbge]`; *fallback* = `municipio` (SICOR) em *Title Case*. Não usar como chave de join. |
| `programa` | `texto` | — | Programa de crédito rural. | `PRONAF` \| `PRONAMP` \| `DEMAIS`. | BCB/SICOR | **Derivado** de `cdPrograma` (`get_programa_name`): `1`/`0001`→PRONAF, `50`/`0050`→PRONAMP, resto→DEMAIS. |
| `valor` | `decimal` | R$ | Valor contratado total no recorte (soma custeio+investimento+comercialização). | ≥ 0; reais correntes. | BCB/SICOR | `valor_custeio + valor_invest + valor_comerc`. Não deflacionado. |
| `contratos` | `inteiro` | contratos | Nº de operações de crédito no recorte. | ≥ 0. | BCB/SICOR | Soma das contagens por finalidade. |
| `area` | `decimal` | ha | Área financiada no recorte. | ≥ 0. | BCB/SICOR | `area_custeio + area_invest`; só custeio/investimento informam área (comercialização = 0). |
| `regional_idr` | `codigo` | — | Núcleo Regional IDR. **(inferido / derivado)** | 23 regionais; FK → de-para. | IDR-Paraná | Ver §2. Adicionar no ETL para o CSV publicado. |

> **Chave primária (origem):** `(ano, mes, codIbge, programa)`. **Valores em reais correntes**
> (não deflacionados) — para séries comparáveis, deflacionar fora do dataset.

---

## 4. Coleção `byProduto` — crédito por produto agropecuário

Origem: endpoints `CusteioRegiaoUFProduto`, `InvestRegiaoUFProduto`, `ComercRegiaoUFProduto`
(unificados). Nível **regional do BCB** + produto (sem `codIbge`) — **não** mapeia para município.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano de emissão. | `2013`–`2026`. | BCB/SICOR | — |
| `mes` | `inteiro` | mês | Mês de emissão. | `1`–`12`. | BCB/SICOR | — |
| `produto` | `texto` | — | Produto agropecuário financiado (`nomeProduto`). | Texto livre do SICOR (ex.: `SOJA`, `MILHO`, `ABACATE`…). | BCB/SICOR | Aspas removidas no ETL. Padronizável via `mapeamento_vbp.json` (de-para → classes VBP/DERAL). |
| `valor` | `decimal` | R$ | Valor contratado do produto no recorte. | ≥ 0; reais correntes. | BCB/SICOR | Soma das finalidades. |
| `contratos` | `inteiro` | contratos | Nº de operações. | ≥ 0. | BCB/SICOR | — |
| `area` | `decimal` | ha | Área financiada (apenas custeio informa área). | ≥ 0. | BCB/SICOR | `AreaCusteio`; investimento/comercialização = 0. |
| `finalidade` | `texto` | — | Finalidade do crédito (presente na coleção intermediária por produto). | `CUSTEIO` \| `INVESTIMENTO` \| `COMERCIALIZACAO`. | BCB/SICOR | Em `byProduto` é agregado por produto; mantido na origem por finalidade. |
| `regional_idr` | `codigo` | — | **Não aplicável diretamente.** **(inferido)** | — | — | Coleção em nível **regional do BCB**, não municipal; **não derivar** `regional_idr` aqui (ver §8). Publicar como recorte estadual/por produto. |

---

## 5. Coleção `byFinalidade` / `byPrograma` — recortes por finalidade e programa

Origem: `ProgramaSubprogramaRegiaoUF` (nível regional do BCB).

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano de emissão. | `2013`–`2026`. | BCB/SICOR | — |
| `mes` | `inteiro` | mês | Mês de emissão. | `1`–`12`. | BCB/SICOR | — |
| `programa` | `texto` | — | Programa de crédito. | `PRONAF` \| `PRONAMP` \| `DEMAIS`. | BCB/SICOR | Derivado de `cdPrograma`. |
| `finalidade` | `texto` | — | Finalidade do crédito (presente em `byFinalidade`). | `CUSTEIO` \| `INVESTIMENTO` \| `COMERCIALIZACAO`. | BCB/SICOR | A origem `RegiaoUF` traz ainda `INDUSTRIALIZACAO` (`valor_indust`), somada nos totais. |
| `valor` | `decimal` | R$ | Valor contratado no recorte. | ≥ 0; reais correntes. | BCB/SICOR | — |
| `contratos` | `inteiro` | contratos | Nº de operações. | ≥ 0. | BCB/SICOR | — |
| `area` | `decimal` | ha | Área financiada. | ≥ 0 (0 nesta coleção). | BCB/SICOR | Fixado em 0 nestes recortes regionais. |
| `regional_idr` | `codigo` | — | **Não aplicável diretamente.** **(inferido)** | — | — | Nível regional do BCB; ver §8. |

---

## 6. Séries temporais (`byAno`, `byMes`) e totais

Origem: `RegiaoUF` (PR). Visão agregada estadual.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano de emissão. | `2013`–`2026`. | BCB/SICOR | Presente em `byAno`, `byMes`. |
| `mes` | `inteiro` | mês | Mês de emissão. | `1`–`12`. | BCB/SICOR | Presente em `byMes`. |
| `valor` | `decimal` | R$ | Valor contratado total (custeio+invest+comerc+indust). | ≥ 0; reais correntes. | BCB/SICOR | — |
| `contratos` | `inteiro` | contratos | Nº total de operações. | ≥ 0. | BCB/SICOR | — |
| `area` | `decimal` | ha | Área financiada (de `MunicipioUF`, *join* por `ano`/`mes`). | ≥ 0. | BCB/SICOR | 0 quando não há dado municipal correspondente. |
| `rank` | `inteiro` | — | Posição no ranking (em `municipioTotals`, `produtoTotals`). | ≥ 1. | derivado ETL | Só nas coleções `*Totals` e `bump`. |
| `name` / `produto` / `programa` / `finalidade` | `texto` | — | Rótulo da unidade ranqueada (conforme a coleção de totais). | ver seções acima. | BCB/SICOR + IBGE | `municipioTotals` traz `name` + (derivável) `regional_idr`. |

---

## 7. `byGenero`, `forecasts.json` e `mapeamento_vbp.json`

### 7.1 `byGenero` (origem `RegiaoUFGenero`, nível regional do BCB)

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano de emissão. | `2013`–`2026`. | BCB/SICOR | Em `byGenero.byAnoMes`. |
| `mes` | `inteiro` | mês | Mês de emissão. | `1`–`12`. | BCB/SICOR | — |
| `genero` | `texto` | — | Gênero do(a) tomador(a) do crédito. | `feminino` (`cdSexo=1`) \| `masculino` (`cdSexo=2`). | BCB/SICOR | Atributo **agregado** (somatório de valores), não individual — sem identificação pessoal. |
| `valor` | `decimal` | R$ | Valor contratado por gênero no recorte. | ≥ 0; reais correntes. | BCB/SICOR | `totals.masculino`/`totals.feminino` = somatórios do período. |

### 7.2 `forecasts.json` — projeções de modelos (`scripts/generate_forecasts.py`)

Estrutura: `{ total | custeio | investimento | comercializacao } → { xgboost | lightgbm | randomforest } → { predictions[], metrics, mape, rmse, r2 }`.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `ano` | `ano` | ano | Ano projetado. | futuro a partir do último observado. | modelo (ETL) | **Dado modelado, não observado.** |
| `mes` | `inteiro` | mês | Mês projetado. | `1`–`12`. | modelo (ETL) | — |
| `valor` | `decimal` | R$ | Valor contratado previsto (estimativa pontual). | ≥ 0; reais correntes. | modelo (ETL) | XGBoost/LightGBM/RandomForest. |
| `lower_80` / `upper_80` | `decimal` | R$ | Limites do intervalo de previsão a 80%. | ≥ 0. | modelo (ETL) | Banda de incerteza. |
| `lower_95` / `upper_95` | `decimal` | R$ | Limites do intervalo de previsão a 95%. | ≥ 0. | modelo (ETL) | Banda de incerteza. |
| `mape` | `decimal` | % | Erro percentual absoluto médio do modelo. | ≥ 0. | métrica (ETL) | Em `metrics`/raiz do nó do modelo. |
| `rmse` | `decimal` | R$ | Raiz do erro quadrático médio. | ≥ 0. | métrica (ETL) | — |
| `r2` | `decimal` | — | Coeficiente de determinação (R²). | ≤ 1. | métrica (ETL) | Qualidade de ajuste. |

> **Aviso obrigatório:** previsões são **estimativas de modelo**, não dado oficial do BCB.
> Publicar separadamente do dado observado, com a banda de incerteza e as métricas visíveis.

### 7.3 `mapeamento_vbp.json` — de-para de produtos

Objeto `{ "NOME_SICOR": "Classe VBP/DERAL" }` (ex.: `"SOJA EM GRAO" → "Soja"`, `"BOVINOS DE LEITE" → "Leite"`).

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `produto_sicor` | `texto` | — | Nome do produto como vem do SICOR. | chave do objeto. | BCB/SICOR | — |
| `produto_vbp` | `texto` | — | Classe padronizada (alinhável ao VBP/DERAL). | valor do objeto. | DERAL/SEAB (classificação) | Permite cruzar crédito com o eixo `desempenho-economico` (VBP). |

---

## 8. Ressalvas, proveniência e LGPD

- **Granularidade regional ≠ `regional_idr`.** As coleções `RegiaoUF*` (produto, programa,
  finalidade, gênero, séries) usam a **região administrativa do BCB**, que **não** equivale à
  regional do IDR-Paraná. Só a coleção **municipal** (`byMunicipio`, via `codIbge`) permite
  derivar `regional_idr` com segurança. Nas demais, publicar no nível disponível (estado/produto)
  e **não** forçar mapeamento para `regional_idr`.
- **Valores em reais correntes**, não deflacionados. Para comparação intertemporal, deflacionar
  fora do dataset.
- **Formato de origem.** O painel publica JSON pré-agregado (`aggregated.json`, `forecasts.json`,
  `mapeamento_vbp.json`); o Observatório deve gerar **CSV canônico** (UTF-8, sem BOM, `,`/`.`) por
  coleção e adicionar a coluna derivada `regional_idr` no recorte municipal.
- **Licença.** O repositório-fonte declara **MIT** (código). Os **dados** são do **SICOR/BCB**
  (API pública) e seguem os **termos do Banco Central**. A licença de publicação do Observatório
  (`CC BY 4.0`) **fica a confirmar** para o dado redistribuído — preservar a atribuição BCB/SICOR.
- **Proveniência.** Coleta: `scripts/fetch_data.py` (OData BCB, `$filter=nomeUF eq 'PR'`).
  Transformação/agregação: `scripts/preprocess_data.py`. Previsão: `scripts/generate_forecasts.py`.
  Atualização automatizada via GitHub Actions (`.github/workflows/data-pipeline.yml`).

### Nota LGPD (regra dura — `docs/DADOS-ABERTOS.md` §6)

- O SICOR (este painel) já chega **agregado** por ano/mês/município/programa/produto/gênero —
  **sem CPF/CNPJ, sem nome de produtor(a), sem coordenada individual.** Manter assim.
- O campo `genero` é **agregado** (somatório de valores), nunca atributo de pessoa identificada.
- Aplicar **supressão de célula** onde a contagem de contratos por recorte for baixa o suficiente
  para reidentificar; registrar a supressão em `notas` do dataset.
- **Base interna LC-CD (Compra Direta & Leite das Crianças)** — eixo `credito-politicas`, status
  `interno` em `eixos.json` ("cruza CPF/CNPJ"): **só entra no portal como AGREGADO**
  (por município/`regional_idr`/ano/programa). **Jamais** publicar CPF, CNPJ, NIT/CAF, nome de
  beneficiário(a) ou microdado individual. A anonimização/agregação ocorre **no ETL**, antes de
  qualquer arquivo chegar a `assets/data/`; microdado pessoal não deve existir no histórico Git
  público.
