<!--
  Modelo de DICIONÁRIO DE DADOS — Observatório Rural Paranaense.
  Copie este arquivo para assets/data/{eixo}/DICIONARIO.md e preencha com as
  COLUNAS REAIS do dataset (uma linha por coluna). Em paralelo, mantenha o
  espelho de máquina {dataset}.dict.json (gerado por pipeline/export_open_data.py).

  Regras (ver docs/DADOS-ABERTOS.md §3):
    - Idioma pt-BR. Toda coluna documentada (nenhuma coluna do CSV sem linha aqui).
    - Tipos canônicos: inteiro | decimal | texto | data (AAAA-MM-DD) | ano (AAAA)
      | booleano | codigo (string de código, ex.: cod_ibge, creg_idr).
    - Unidade física no padrão: R$, ha, t, kg, %, un, — (sem unidade).
    - Atribuir `fonte` por coluna (origem específica daquela coluna).
    - `regional_idr` (FK -> geo/municipios_ref_idr.csv, creg_idr) é a chave de
      agregação regional canônica; datasets municipais carregam `cod_ibge`.
    - Campos não confirmados na fonte: marque a descrição/nota com "(inferido)";
      NÃO invente domínio/fonte.
    - LGPD: o dataset só contém AGREGADOS; nunca CPF/CNPJ/identificador pessoal.
  Remova estes comentários ao publicar.
-->

# Dicionário de dados — {Título legível do dataset}

- **Dataset:** `{eixo}/{dataset}`  <!-- ex.: desempenho-economico/vbp-municipios -->
- **Versão:** {MAJOR.MINOR}          <!-- bump MAJOR se o esquema/colunas mudou -->
- **Fonte:** {origem primária}        <!-- ex.: DERAL/SEAB — Valor Bruto da Produção -->
- **Órgão:** {instituição responsável} <!-- ex.: IDR-Paraná / SEAB -->
- **Periodicidade:** {anual | mensal | diaria | semanal | eventual | unica}
- **Cobertura temporal:** {AAAA}–{AAAA}
- **Cobertura geográfica:** {estado | mesorregião | regional_idr | município} ({n} unidades)
- **Última atualização:** {AAAA-MM-DD}
- **Licença:** CC BY 4.0 (Creative Commons Atribuição 4.0)

## Colunas

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `cod_ibge` | `codigo` | — | Código IBGE do município (7 dígitos). | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE — Malha Municipal | Presente quando a granularidade é municipal. Compõe a chave primária. |
| `regional_idr` | `codigo` | — | Núcleo Regional do IDR-Paraná (chave de agregação regional). | 23 regionais (`"01"`–`"23"`, sem `"08"`); FK → `geo/municipios_ref_idr.csv` (`creg_idr`). | IDR-Paraná | String com zero à esquerda. Derivado de `cod_ibge` no ETL (junção por chave, nunca por nome). |
| `{nome_coluna}` | `{inteiro\|decimal\|texto\|data\|ano\|booleano\|codigo}` | `{R$\|ha\|t\|%\|—}` | {o que a coluna representa} | {valores válidos / faixa / enum / FK} | {origem específica da coluna} | {ressalvas, precisão, nulos, supressão LGPD; "(inferido)" se não confirmado} |

## Notas metodológicas

<!--
  Registre aqui o que o leitor precisa para usar o dado corretamente, por ex.:
    - reais correntes vs. deflacionados; ano-safra vs. ano-calendário;
    - supressão de células pequenas aplicada (n < limiar) por LGPD;
    - quebras de série, mudanças de classificação, valores nulos/ausentes;
    - como `regional_idr` foi derivado (de-para `municipios_ref_idr.csv`).
-->

- {observação 1}
- {observação 2}

## Proveniência

- **Pipeline:** `pipeline/ingest.py` → `pipeline/model.py` → `pipeline/export_open_data.py`.
- **De-para geográfico:** `assets/data/geo/municipios_ref_idr.csv` (única fonte do mapeamento município → regional → mesorregião).
- **Entrada de catálogo:** `assets/data/catalog.json` (`id = {eixo}/{dataset}`).
