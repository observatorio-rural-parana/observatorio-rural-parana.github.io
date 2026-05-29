# Dicionário de dados — Valor Bruto da Produção (VBP) do Paraná

> Eixo: **desempenho-economico** · Dataset: `vbp-parana` · Versão: 1.0
> Fonte primária: **DERAL/SEAB · IDR-Paraná** (Valor Bruto da Produção Agropecuária).
> Painel de origem: [`avnergomes/vbp-parana`](https://github.com/avnergomes/vbp-parana)
> ([dashboard](https://avnergomes.github.io/vbp-parana/)).
> Idioma: pt-BR. Formato canônico: CSV UTF-8 (sem BOM, separador `,`, decimal `.`).
> Chave geográfica canônica do Observatório: **`regional_idr`** (399 municípios →
> 23 regionais → 7 mesorregiões — ver `docs/GEO.md`).

## Sobre o extrato padronizado

Este extrato (`vbp.csv` / `vbp.json`) é a **agregação municipal por ano** do VBP
agropecuário paranaense (todos os produtos somados por município/ano), derivada da
tabela real `mapData` do arquivo processado
[`dashboard/public/data/detailed.json`](https://raw.githubusercontent.com/avnergomes/vbp-parana/main/dashboard/public/data/detailed.json)
do painel `avnergomes/vbp-parana`. A coluna canônica **`regional_idr`** (código do
núcleo regional IDR, `creg_idr` 01–23) é anexada por **JOIN por `cod_ibge`** com o
de-para canônico `assets/data/geo/municipios_ref_idr.csv` (nunca por nome de
município). O painel armazena `regional_idr` como **nome** do núcleo; aqui esse nome
é preservado em `reg_idr_nome` (rótulo humano) e o **código** canônico passa a ocupar
`regional_idr`, conforme a convenção do hub.

Granularidade: uma linha por **(`cod_ibge`, `ano`)**. Cobertura: 399 municípios ×
2012–2024 = 5.187 linhas. Os valores de VBP estão em **R$ correntes** (não
deflacionados) e foram **arredondados para inteiro** no pipeline de origem
(`scripts/preprocess_data.py`, função `generate_detailed_data`). A produção é a soma
em **toneladas** após conversão de unidades feita pelo pipeline de origem (litros, kg,
mil litros → t; unidades não-mássicas como UN/CX/DZ/M³/CAB entram como 0 e portanto
**não** são somadas na coluna de produção).

## Tabela do dicionário

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `cod_ibge` | `codigo` | — | Código IBGE do município (7 dígitos, string com zero à esquerda). | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE — Malha Municipal | Compõe a chave primária `(cod_ibge, ano)`. Tratar sempre como string. |
| `municipio` | `texto` | — | Nome do município conforme o painel de origem. | Texto controlado pelo de-para geográfico. | DERAL/SEAB (rótulo do painel) | Redundante com `cod_ibge`; mantido por legibilidade. **Não usar como chave de join** (acentuação/grafia divergem entre fontes — usar `cod_ibge`). |
| `regional_idr` | `codigo` | — | **Chave geográfica canônica do Observatório**: código do núcleo regional IDR. | `01`–`23` (sem `08` — lacuna histórica esperada, ver `docs/GEO.md`); FK → `geo/municipios_ref_idr.csv` (`creg_idr`). | IDR-Paraná | Derivado no ETL a partir de `cod_ibge` via de-para. String com zero à esquerda (`"02"`); chave de agregação regional/mesorregional. |
| `reg_idr_nome` | `texto` | — | Nome (sede) do núcleo regional IDR — rótulo humano de `regional_idr`. | 23 núcleos (ex.: `Cornélio Procópio`, `Toledo`, `Cascavel`); FK → `geo/municipios_ref_idr.csv` (`reg_idr`). | IDR-Paraná | Rótulo de exibição; junções por `regional_idr` (código), não por este nome. |
| `meso_idr` | `texto` | — | Mesorregião IDR a que o município pertence. | 7 valores: `Norte`, `Metropolitana e Litoral`, `Oeste`, `Noroeste`, `Sudoeste`, `Centro Sul`, `Centro`; FK → `geo/municipios_ref_idr.csv` (`meso_idr`). | IDR-Paraná | Regionalização do IDR (**não** as mesorregiões do IBGE). Nível superior de agregação. |
| `ano` | `ano` | ano | Ano de referência do VBP. | `2012`–`2024`. | DERAL/SEAB | Ano de referência conforme metodologia DERAL (planilhas anuais VBP2012–vbp2024). |
| `vbp_reais` | `inteiro` | R$ | Valor Bruto da Produção agropecuária do município no ano (soma de todos os produtos). | ≥ 0; reais correntes (não deflacionado). | DERAL/SEAB | Arredondado para inteiro no pipeline de origem. Para séries comparáveis, **deflacionar fora do dataset** (deflator não embutido). Pode haver supressão por sigilo na origem. |
| `producao_ton` | `inteiro` | t | Produção física total do município no ano, convertida para toneladas. | ≥ 0. | DERAL/SEAB (conversão pelo ETL de origem) | Soma **apenas** de itens com unidade mássica (TON/T, KG, L≈1 kg/L, MIL L); itens em UN/CX/DZ/M³/M²/VSO/MCO/CAB entram como 0 e **não** somam. Mistura cadeias heterogêneas — usar com ressalva metodológica. (parcialmente inferido — regra de conversão lida em `preprocess_data.py`). |
| `area_ha` | `inteiro` | ha | Área total associada à produção do município no ano. | ≥ 0. | DERAL/SEAB | Arredondado para inteiro no pipeline de origem. Soma áreas de lavouras/usos heterogêneos do ano. (inferido — rótulo de unidade `ha` assumido a partir da coluna `area`/`area_(ha)` do pipeline de origem). |

### Observação metodológica obrigatória

- **Valores em reais correntes** (não deflacionados): para comparação temporal,
  aplicar deflator (ex.: IGP-DI/IPCA) **fora** deste dataset.
- **`producao_ton` não é total físico completo**: por construção do pipeline de
  origem, produtos cuja unidade não é de massa (unidades, caixas, dúzias, m³, etc.)
  entram com 0 na conversão e não compõem a soma. Use para ordens de grandeza,
  não como total físico exato da produção municipal.
- **LGPD**: dataset 100% agregado (município × ano); sem CPF/CNPJ ou identificação
  de produtor — conforme `docs/DADOS-ABERTOS.md` §6.

## Procedência e reprodutibilidade

- **Fonte primária do dado:** Valor Bruto da Produção Agropecuária — DERAL/SEAB
  (Departamento de Economia Rural / Secretaria da Agricultura e do Abastecimento do
  Paraná) e IDR-Paraná. Período 2012–2024.
- **Arquivos brutos (origem):** planilhas Excel anuais `data/VBP2012.xlsx … vbp2024.xlsx`
  no repositório `avnergomes/vbp-parana`, mais `lista_produtos_vbp_2012_2024.xlsx`
  (catálogo de cadeias/subcadeias) e `municipios_pr.xlsx` (referência municipal).
- **Processamento de origem:** `scripts/preprocess_data.py` (Python/pandas) gera
  `dashboard/public/data/aggregated.json` e `detailed.json`. Este extrato usa a tabela
  `mapData` de `detailed.json` (VBP por município × ano).
- **Fonte completa (não amostrada):** todas as 5.187 linhas (399 mun. × 2012–2024)
  estão em `vbp.csv`/`vbp.json` deste diretório. A amostra fiel
  (`vbp.sample.csv`/`.json`) traz os anos-âncora 2012 e 2024 para os 399 municípios.
- **Granularidade adicional disponível na origem (não publicada aqui):**
  `detailed.json` traz ainda `byAnoProdutoMunicipio` (VBP por ano × produto ×
  município, ~439 mil linhas) e cortes por cadeia/subcadeia/regional; `aggregated.json`
  traz séries e rankings. Para o extrato municipal canônico do eixo, usamos a
  agregação por município/ano.
- **Licença:** o **código** do painel é MIT (© 2024–2026 Avner Gomes). O **dado** é de
  origem governamental (DERAL/SEAB · IDR-Paraná); no portal adota-se o padrão
  **CC BY 4.0** com atribuição à fonte — **a confirmar** junto à SEAB/IDR via convênio
  formal de dados (ver `docs/PROJETO-BRIEF.md`, decisão nº 1).

## Como reproduzir

O script `_build_extract.py` (neste diretório) baixa a fonte real
(`detailed.json` → `mapData`), faz o JOIN por `cod_ibge` com
`assets/data/geo/municipios_ref_idr.csv` para anexar `regional_idr`/`meso_idr` e
regenera `vbp.csv`, `vbp.json`, `vbp.sample.csv`, `vbp.sample.json`.

```bash
python _build_extract.py
```
