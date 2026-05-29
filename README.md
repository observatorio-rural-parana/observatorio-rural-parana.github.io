# Observatório Rural Paranaense

> **Inteligência de dados da agropecuária e do desenvolvimento rural do Paraná — aberta, integrada e institucional.**

Hub público que reúne, sob uma única marca de governo, o ecossistema de painéis
dinâmicos do agro paranaense. Mais do que agregar visualizações, o Observatório
publica **dados abertos** (download em formato aberto + dicionário de dados) como
diferencial central: transparência, reprodutibilidade e reúso por gestores,
pesquisadores, produtores e sociedade.

---

## O que é

O Observatório Rural Paranaense é, ao mesmo tempo:

- **Hub agregador** — porta de entrada institucional que organiza painéis,
  indicadores e séries históricas do agro do Paraná por eixos temáticos,
  navegáveis a partir de uma taxonomia única.
- **Plataforma de dados abertos** — cada painel disponibiliza seus dados em
  formatos abertos (CSV / XLSX / JSON) acompanhados de **dicionário de dados**,
  com atribuição explícita de fontes.

A vocação é editorial e institucional: sóbrio, imprimível, acessível (WCAG AA) e
fiel à identidade visual oficial do Governo do Paraná, da SEAB e do IDR-Paraná.

### Modelo de referência e sistema-fonte

- **Modelo de referência:** Observatório Agro Catarinense (Cepa/Epagri) — referência
  consolidada de observatório agropecuário estadual, que inspira escopo, organização
  por eixos e a prática de dados abertos.
- **Sistema-fonte (SEAGRI-PR):** o arranjo institucional paranaense que alimenta o
  Observatório, composto por **SEAB**, **IDR-Paraná**, **CEASA-PR** e **ADAPAR**,
  complementado por fontes federais e de pesquisa (IBGE, BCB, MDIC, IPARDES, entre outras).

---

## As 4 decisões travadas

Estas decisões (firmadas em 2026-05-29) orientam toda contribuição ao repositório.
A fonte canônica está em [`docs/PROJETO-BRIEF.md`](docs/PROJETO-BRIEF.md).

1. **Caráter institucional oficial (IDR / SEAB).** É marca de governo, não um projeto
   pessoal. Equipe e fomento via Edital Push Innovation / FAPEAGRO; convênios formais
   para o uso de dados.
2. **Padronizar sob a nova org antes de publicar.** Não basta linkar painéis: define-se
   um *cookiecutter* de painel, stack unificada e disciplina de dados abertos, na org
   dedicada `observatorio-rural-parana` (até haver domínio `.pr.gov.br`).
3. **Design system único, com pendor editorial.** Estilo "jornal-creme" + verdes IDR,
   centralizado em [`assets/css/tokens.css`](assets/css/tokens.css). Toda cor, tipografia
   e espaçamento vêm de tokens — nunca valores soltos.
4. **Dados abertos: SIM.** CSV / XLSX / JSON + dicionário de dados por painel, com
   atribuição de fontes sempre explícita.

---

## Os 11 eixos temáticos

A taxonomia completa — eixos, painéis, status, fontes e camadas contextuais — é lida
de [`assets/data/eixos.json`](assets/data/eixos.json). **Não** hardcode painéis em
HTML/JS: consuma sempre esse arquivo. O resumo abaixo é apenas orientativo; em caso de
divergência, prevalece o `eixos.json`.

Os **5 eixos-piloto** (primeira onda de publicação) estão marcados com ★.

|  # | Eixo                                              | Piloto | `id`                          |
|---:|---------------------------------------------------|:------:|-------------------------------|
|  1 | Produção Agropecuária                             |        | `producao-agropecuaria`       |
|  2 | Desempenho Econômico do Agro                      |   ★    | `desempenho-economico`        |
|  3 | Mercado e Preços                                  |   ★    | `mercado-precos`              |
|  4 | Comércio Exterior do Agronegócio                  |   ★    | `comercio-exterior`           |
|  5 | Crédito e Políticas Públicas Rurais               |   ★    | `credito-politicas`           |
|  6 | Assistência Técnica e Extensão Rural (ATER)       |   ★    | `ater`                        |
|  7 | Desenvolvimento Rural e Socioeconômico            |        | `desenvolvimento-rural`       |
|  8 | Recursos Hídricos, Ambiental e Geoespacial        |        | `recursos-hidricos-ambiental` |
|  9 | Sanidade e Defesa Agropecuária                    |        | `sanidade-defesa`             |
| 10 | Clima e Agrometeorologia                          |        | `clima-agrometeorologia`      |
| 11 | Infraestrutura e Energia Rural                    |        | `infraestrutura-energia`      |

Além dos 11 eixos, a taxonomia contempla **2 camadas contextuais** (Saúde e Segurança,
como contexto rural) e um **núcleo de inteligência territorial** (índice IRTC, 399
municípios). Consulte [`assets/data/eixos.json`](assets/data/eixos.json) para os detalhes.

**Legenda de status** (conforme `eixos.json`): `ativo` (painel já publicado no
ecossistema) · `planejado` (a construir a partir do cookiecutter) · `contextual`
(camada transversal de apoio, não-agro) · `interno` (uso restrito / LGPD — apenas
agregados no portal público).

---

## Geografia

A chave geográfica única é `regional_idr`, organizando o território em quatro níveis:
**estado → 7 mesorregiões → 23 regionais IDR → 399 municípios**. O de-para de
municípios e os limites geográficos são versionados em `assets/data/geo/`.
Detalhes em [`docs/GEO.md`](docs/GEO.md).

---

## Como o repositório se organiza

```
observatorio-rural-parana.github.io/
├── index.html              # página inicial do hub (a publicar — Fase 0)
├── .nojekyll               # serve estático sem processamento Jekyll
├── assets/
│   ├── css/
│   │   └── tokens.css      # design system — fonte única da verdade (use var(--…))
│   ├── js/                 # comportamento vanilla (sem framework)
│   ├── data/
│   │   ├── eixos.json      # taxonomia de eixos e painéis (fonte da verdade)
│   │   └── geo/            # de-para de municípios e camadas geográficas (regional_idr)
│   └── logos/              # logos oficiais IDR e Gov-PR/SEAB (+ logos_b64.json)
├── docs/                   # documentação de projeto (briefs, roadmap, arquitetura)
│   └── PROJETO-BRIEF.md    # contexto, decisões e convenções
└── .github/
    └── workflows/          # CI (link-check, validação de dados, publicação Pages)
```

> Convenção de stack: **HTML / CSS / JS vanilla** (sem framework) no hub, servido como
> site estático via GitHub Pages. Toda cor e tipografia vêm de `tokens.css`; toda lista
> de painéis é lida de `eixos.json`.

---

## Como rodar localmente

O hub é um site estático: basta servir a raiz do repositório com qualquer servidor
HTTP local. Com o Python instalado:

```bash
# a partir da raiz do repositório
python -m http.server 8000
```

Depois, abra <http://localhost:8000> no navegador.

Alternativas equivalentes:

```bash
# Node (npx, sem instalação global)
npx serve .

# PHP
php -S localhost:8000
```

> Evite abrir `index.html` via `file://`: os carregamentos de `eixos.json` e demais
> dados dependem de requisições HTTP, que não funcionam sob o protocolo de arquivo.

---

## Status atual

**Fase 0 — Fundação.** Em construção a base do hub: design system (`tokens.css`),
taxonomia de eixos (`eixos.json`), backbone geográfico, logos oficiais e documentação.
A primeira onda de publicação cobrirá os **5 eixos-piloto** indicados acima.

### Documentação e próximos passos

À medida que a Fase 0 avança, esta documentação é incrementada. Ponteiros de referência:

- [`docs/PROJETO-BRIEF.md`](docs/PROJETO-BRIEF.md) — contexto, decisões e convenções (já disponível).
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — fases, marcos e ondas de publicação.
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — stack, cookiecutter de painel, segurança e integração.
- [`docs/DADOS-ABERTOS.md`](docs/DADOS-ABERTOS.md) — política de dados abertos, formatos e dicionário de dados.
- [`docs/GEO.md`](docs/GEO.md) — chave `regional_idr`, níveis territoriais e camadas geográficas.
- [`docs/EIXOS.md`](docs/EIXOS.md) — detalhamento dos eixos, painéis e fontes.

---

## Licença e créditos

> **Placeholder — a confirmar.** Iniciativa institucional do **Governo do Paraná**,
> conduzida pela **SEAB** e pelo **IDR-Paraná**. A licença do código e a licença de uso
> dos dados (com atribuição de fontes) serão definidas conforme os convênios formais de
> dados e a política institucional.

A atribuição das fontes de cada conjunto de dados é sempre explícita, em nome da
transparência e da reprodutibilidade.
