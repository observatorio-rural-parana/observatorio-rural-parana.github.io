# Eixos Temáticos — Observatório Rural Paranaense

> Documento da **taxonomia temática** do hub. Fonte da verdade: `assets/data/eixos.json`.
> Qualquer página, doc ou agente deve ler a lista de eixos e painéis **de** `eixos.json` —
> este documento descreve e explica essa taxonomia, mas **não** a substitui nem inventa painéis.
> Em caso de divergência, `eixos.json` prevalece.

- **Projeto:** Observatório Rural Paranaense
- **Org / hub:** `observatorio-rural-parana` / `observatorio-rural-parana.github.io`
- **Modelo de referência:** Observatório Agro Catarinense (Cepa/Epagri)
- **Sistema-fonte:** SEAGRI-PR (SEAB · IDR-Paraná · CEASA-PR · ADAPAR)

A taxonomia é composta por **11 eixos temáticos** + **2 camadas contextuais** + **1 núcleo
de inteligência**. Cinco eixos são **piloto** (primeira onda de publicação):
`desempenho-economico`, `mercado-precos`, `comercio-exterior`, `credito-politicas` e `ater`.

---

## Alinhamento: modelo catarinense (7 áreas) + eixos específicos do PR

O Observatório Agro Catarinense (Cepa/Epagri) organiza seu conteúdo em torno de **7 grandes
áreas**. A taxonomia do Observatório Rural Paranaense adota essas áreas como espinha dorsal e
acrescenta **eixos específicos do Paraná**, exigidos pela estrutura institucional
SEAGRI-PR (SEAB · IDR-Paraná · CEASA-PR · ADAPAR) e pelo ecossistema de painéis já existente.

### As 7 áreas do modelo catarinense e como se mapeiam no PR

| # | Área (modelo catarinense) | Eixo(s) correspondente(s) no PR |
|---|---------------------------|---------------------------------|
| 1 | Produção agropecuária | **Produção Agropecuária** (`producao-agropecuaria`) |
| 2 | Desempenho econômico do agro | **Desempenho Econômico do Agro** (`desempenho-economico`) |
| 3 | Mercado e preços | **Mercado e Preços** (`mercado-precos`) |
| 4 | Comércio exterior | **Comércio Exterior do Agronegócio** (`comercio-exterior`) |
| 5 | Crédito e políticas públicas | **Crédito e Políticas Públicas Rurais** (`credito-politicas`) |
| 6 | Assistência técnica e extensão rural | **Assistência Técnica e Extensão Rural (ATER)** (`ater`) |
| 7 | Desenvolvimento rural e socioeconômico | **Desenvolvimento Rural e Socioeconômico** (`desenvolvimento-rural`) |

Esses 7 eixos cobrem integralmente o escopo do modelo de referência. Os **6 primeiros**
formam, com exceção da Produção Agropecuária, o conjunto-piloto (5 eixos), por já contarem com
painéis ativos no ecossistema.

### Eixos específicos do Paraná (além do modelo catarinense)

Quatro eixos adicionais respondem a competências e bases de dados próprias do arranjo
institucional paranaense (IAT, ADAPAR, IDR-Agrometeorologia, CIBIOGÁS, entre outros):

| # | Eixo específico do PR | Justificativa institucional |
|---|------------------------|------------------------------|
| 8 | **Recursos Hídricos, Ambiental e Geoespacial** (`recursos-hidricos-ambiental`) | Microbacias/ottobacias, água segura, CAR e uso do solo — bases do IAT, Sanepar/Águas-PR, ANA e MapBiomas. |
| 9 | **Sanidade e Defesa Agropecuária** (`sanidade-defesa`) | Trânsito (GTA/PTV), agrotóxicos (SIAGRO) e pragas — competência da ADAPAR. |
| 10 | **Clima e Agrometeorologia** (`clima-agrometeorologia`) | Rede de estações do IDR-Paraná, SIMEPAR e INMET — alertas e risco climático. |
| 11 | **Infraestrutura e Energia Rural** (`infraestrutura-energia`) | Armazenagem, biogás/bioenergia e estradas rurais — SEAB, IBGE/PPM e CIBIOGÁS. |

> **Camadas contextuais e núcleo de inteligência** (Saúde, Segurança e Inteligência
> Territorial) **não** integram as 7 áreas do modelo catarinense: são apoio transversal e
> camada analítica próprios do projeto do PR. Ver seções dedicadas abaixo.

---

## Tabela-resumo dos 11 eixos

Contagens derivadas diretamente de `eixos.json`. "Ativos" conta painéis com `status: "ativo"`;
"Planejados" conta `status: "planejado"`. Painéis `interno` (LGPD / só agregados) são
contabilizados à parte na coluna de observações.

| Ordem | Eixo | Piloto | Painéis ativos | Painéis planejados |
|:-----:|------|:------:|:--------------:|:------------------:|
| 1 | Produção Agropecuária | Não | 1 | 1 |
| 2 | Desempenho Econômico do Agro | **Sim** | 1 | 0 |
| 3 | Mercado e Preços | **Sim** | 3 | 0 |
| 4 | Comércio Exterior do Agronegócio | **Sim** | 1 | 0 |
| 5 | Crédito e Políticas Públicas Rurais | **Sim** | 1 | 0 ¹ |
| 6 | Assistência Técnica e Extensão Rural (ATER) | **Sim** | 2 | 0 |
| 7 | Desenvolvimento Rural e Socioeconômico | Não | 2 | 0 |
| 8 | Recursos Hídricos, Ambiental e Geoespacial | Não | 3 | 0 |
| 9 | Sanidade e Defesa Agropecuária | Não | 0 | 1 |
| 10 | Clima e Agrometeorologia | Não | 0 | 1 |
| 11 | Infraestrutura e Energia Rural | Não | 0 | 1 |
| | **Total** | **5 piloto** | **14** | **5** ¹ |

¹ Além dos painéis ativos/planejados, o eixo **Crédito e Políticas Públicas Rurais** possui
1 painel com status **`interno`** (Compra Direta & Leite das Crianças), publicável apenas como
agregados no portal público (LGPD).

### Legenda de status

| Status | Significado |
|--------|-------------|
| `ativo` | Painel já publicado e no ar no ecossistema (URL a confirmar via link-check). |
| `planejado` | Eixo/painel a construir a partir do cookiecutter. |
| `contextual` | Camada transversal de apoio (não-agro). |
| `interno` | Uso restrito / LGPD — só agregados no portal público. |

---

## Os 11 eixos em detalhe

### 1. Produção Agropecuária

- **`id`:** `producao-agropecuaria`
- **Ordem:** 1
- **Piloto:** Não
- **Descrição:** Produção vegetal (grãos, fruticultura, olericultura), pecuária (carnes,
  leite, ovos, mel, rebanhos), florestal (silvicultura/extração) e aquicultura/pesca.
- **Fontes (órgão/sistema):** IBGE LSPA/PAM/PPM/Censo Agropecuário · DERAL Estimativa de Safra

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Integração ILPF (carne & madeira) | `avnergomes/carne_madeira` | `ativo` | https://avnergomes.github.io/carne_madeira/ |
| Produção vegetal e pecuária | — | `planejado` | — |

---

### 2. Desempenho Econômico do Agro

- **`id`:** `desempenho-economico`
- **Ordem:** 2
- **Piloto:** **Sim**
- **Descrição:** Valor Bruto da Produção (VBP), Valor Adicionado Bruto (VAB), PIB do agro,
  área e produtividade. Indicador-âncora — compõe a partilha do ICMS estadual.
- **Fontes (órgão/sistema):** DERAL/SEAB · IBGE · IPARDES

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| VBP do Paraná (2012–2024) | `avnergomes/vbp-parana` | `ativo` | https://avnergomes.github.io/vbp-parana/ |

---

### 3. Mercado e Preços

- **`id`:** `mercado-precos`
- **Ordem:** 3
- **Piloto:** **Sim**
- **Descrição:** Preços diários (SIMA), atacado/varejo (CEASA-PR), preços florestais, preços
  de terras, custos de produção e sazonalidade.
- **Fontes (órgão/sistema):** DERAL/SIMA (celepar7.pr.gov.br) · CEASA-PR · DEFLOP · SIPT

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Preços diários (SIMA) | `avnergomes/precos-diarios` | `ativo` | https://avnergomes.github.io/precos-diarios/ |
| Preços florestais (1997–2025) | `avnergomes/precos-florestais` | `ativo` | https://avnergomes.github.io/precos-florestais/ |
| Preços de terras (SIPT 1998–2025) | `avnergomes/precos-de-terras` | `ativo` | https://avnergomes.github.io/precos-de-terras/ |

> Observação: o painel **Preços diários (SIMA)** possui API auxiliar (`api: "Flask/Render"`),
> conforme registrado em `eixos.json`.

---

### 4. Comércio Exterior do Agronegócio

- **`id`:** `comercio-exterior`
- **Ordem:** 4
- **Piloto:** **Sim**
- **Descrição:** Exportações/importações FOB, balança comercial, cadeias por NCM e municípios
  exportadores do agro paranaense.
- **Fontes (órgão/sistema):** MDIC/ComexStat (filtro PR)

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| ComexStat Paraná (2020–2025) | `avnergomes/comexstat-parana` | `ativo` | https://avnergomes.github.io/comexstat-parana/ |

---

### 5. Crédito e Políticas Públicas Rurais

- **`id`:** `credito-politicas`
- **Ordem:** 5
- **Piloto:** **Sim**
- **Descrição:** Crédito rural (SICOR/Pronaf/PNCF) e programas estaduais: Banco do
  Agricultor, Seguro Rural, Trator Solidário, Compra Direta, Leite das Crianças, Terra Boa.
- **Fontes (órgão/sistema):** BCB/SICOR · SEAB/DPA

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Crédito Rural Paraná (SICOR 2013–2026) | `avnergomes/credito-rural-parana` | `ativo` | https://avnergomes.github.io/credito-rural-parana/ |
| Compra Direta & Leite das Crianças (relatórios) | — | `interno` | — |

> Observação: o painel **Compra Direta & Leite das Crianças** tem `status: "interno"` — base
> LC-CD que cruza CPF/CNPJ; publicar **só agregados** no portal público (LGPD).

---

### 6. Assistência Técnica e Extensão Rural (ATER)

- **`id`:** `ater`
- **Ordem:** 6
- **Piloto:** **Sim**
- **Descrição:** Cobertura SISATER, Rede Paranaense de ATER, Relatórios Técnicos de Vistoria
  (RTV) e programas setoriais do IDR.
- **Fontes (órgão/sistema):** IDR-Paraná (SISATER/GETEC)

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Rede Paranaense de ATER | `rededeaterparana/rededeaterparana.github.io` | `ativo` | https://rededeaterparana.github.io/ |
| Relatórios Técnicos de Vistoria (RTV) | `avnergomes/rtv` | `ativo` | https://avnergomes.github.io/rtv/ |

---

### 7. Desenvolvimento Rural e Socioeconômico

- **`id`:** `desenvolvimento-rural`
- **Ordem:** 7
- **Piloto:** Não
- **Descrição:** Demografia/censos, IDHM, estrutura fundiária, emprego no agro, dinâmica
  rural-urbana e agricultura familiar (CAF).
- **Fontes (órgão/sistema):** IBGE (Censos) · RAIS/CAGED · IPARDES

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Censo Paraná (1991–2022) | `avnergomes/censo-parana` | `ativo` | https://avnergomes.github.io/censo-parana/ |
| Emprego no Agro (RAIS/CAGED) | `avnergomes/emprego-agro-parana` | `ativo` | https://avnergomes.github.io/emprego-agro-parana/ |

---

### 8. Recursos Hídricos, Ambiental e Geoespacial

- **`id`:** `recursos-hidricos-ambiental`
- **Ordem:** 8
- **Piloto:** Não
- **Descrição:** Microbacias/ottobacias, água segura, segurança hídrica, CAR, uso do solo,
  MapBiomas, conservação de solo e água.
- **Fontes (órgão/sistema):** IAT · Sanepar/Águas-PR · ANA · MapBiomas · CAR/SICAR

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Água Segura | `avnergomes/aguasegura` | `ativo` | https://avnergomes.github.io/aguasegura/ |
| Programa de Segurança Hídrica (PSH) | `avnergomes/psh` | `ativo` | https://avnergomes.github.io/psh/ |
| Camadas base PR (altimetria/hidrografia/CAF) | `avnergomes/prns` | `ativo` | https://avnergomes.github.io/prns/ |

---

### 9. Sanidade e Defesa Agropecuária

- **`id`:** `sanidade-defesa`
- **Ordem:** 9
- **Piloto:** Não
- **Descrição:** Trânsito (GTA/PTV), vacinação/rebanho, agrotóxicos (SIAGRO) e ocorrência de
  pragas georreferenciada.
- **Fontes (órgão/sistema):** ADAPAR (painéis Power BI/Looker; microdados via LAI)

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Painéis ADAPAR (GTA, agrotóxicos, pragas) | — | `planejado` | — |

> Observação: integrar/espelhar painéis públicos da ADAPAR.

---

### 10. Clima e Agrometeorologia

- **`id`:** `clima-agrometeorologia`
- **Ordem:** 10
- **Piloto:** Não
- **Descrição:** Boletins, mapas de desvio, alertas de geada/estiagem/ondas de calor e risco
  climático.
- **Fontes (órgão/sistema):** IDR-Paraná Agrometeorologia (rede de estações) · SIMEPAR · INMET

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Agroclima Paraná | — | `planejado` | — |

---

### 11. Infraestrutura e Energia Rural

- **`id`:** `infraestrutura-energia`
- **Ordem:** 11
- **Piloto:** Não
- **Descrição:** Armazenagem, biogás/bioenergia, estradas rurais e unidades de processamento.
- **Fontes (órgão/sistema):** SEAB · ADAPAR · IBGE/PPM · CIBIOGÁS

| Painel | Repositório | Status | URL |
|--------|-------------|:------:|-----|
| Panorama do Biogás no Paraná | — | `planejado` | — |

> Observação: base CIBIOGÁS (local) — portar como painel + publicação.

---

## Camadas contextuais (transversais, não-agro)

As camadas contextuais oferecem apoio transversal ao recorte rural, sem integrar o escopo
agropecuário central. Status: `contextual`.

| Camada | `id` | Repositório | Status | Fontes | URL |
|--------|------|-------------|:------:|--------|-----|
| Saúde (contexto rural) | `saude` | `avnergomes/saude-parana` | `contextual` | DATASUS | https://avnergomes.github.io/saude-parana/ |
| Segurança (contexto rural) | `seguranca` | `avnergomes/seguranca-parana` | `contextual` | SESP · IPARDES | https://avnergomes.github.io/seguranca-parana/ |

---

## Núcleo de inteligência

Camada analítica que cruza dados dos eixos para gerar índices territoriais.

- **Nome:** Inteligência Territorial (índice IRTC, 399 municípios)
- **Repositório:** `avnergomes/c2-parana`
- **Status:** `planejado`
- **Observação:** integrar **após** rotação de secrets, remoção de gating e de dados
  sintéticos hardcoded — ver `docs/ARQUITETURA.md §Segurança`.

---

## Notas de manutenção

- **Coerência obrigatória:** toda alteração de eixo, painel, status, repo ou URL deve ser
  feita **primeiro** em `assets/data/eixos.json`; este documento é atualizado em seguida para
  refletir a mesma informação. Não hardcodar painéis em HTML — as páginas leem `eixos.json`.
- **Geo:** chave única `regional_idr` (399 municípios → 23 regionais → 7 mesorregiões).
  Ver `docs/GEO.md`.
- **Atribuição de fontes:** sempre explícita por painel/eixo (transparência e
  reprodutibilidade), conforme `docs/PROJETO-BRIEF.md`.
