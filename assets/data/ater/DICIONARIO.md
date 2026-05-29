# Dicionário de dados — Assistência Técnica e Extensão Rural (ATER)

> Eixo: **`ater`** (`assets/data/eixos.json`, ordem 6, piloto).
> Dataset: **`ater/rede-ater`** — entidades prestadoras de ATER do Paraná, em
> recorte **agregado** (1 linha por entidade), derivado do painel primário
> **Rede Paranaense de ATER** (`rededeaterparana/rededeaterparana.github.io`).
>
> Fonte da verdade do esquema-fonte: `apps-script/Sheets.gs` (constante `SCHEMA`),
> `apps-script/Code.gs` (`lerAgregadoPublico` / `doGet`), `painel/src/lib/api.ts`
> (interface `EntidadePublica`) e `docs/campos.md` do repositório de origem.
>
> Convenções herdadas (ver `docs/PROJETO-BRIEF.md`, `docs/DADOS-ABERTOS.md`,
> `docs/GEO.md`): conteúdo pt-BR; chave geográfica única **`regional_idr`**
> (399 municípios → 23 regionais → 7 mesorregiões); CSV UTF-8 como formato
> canônico; atribuição de fonte explícita; **somente agregados** (LGPD).

---

## 1. Origem e natureza do dado

O painel primário **Rede Paranaense de ATER** cadastra entidades prestadoras de
ATER que aderem à rede (formulário público → Google Apps Script → Google Sheets
privada). O backend expõe publicamente **apenas um subconjunto agregado**
(`doGet?action=listar` → função `lerAgregadoPublico`), nunca o microdado.

Este dataset do Observatório materializa esse agregado público como arquivo
aberto (`rede-ater.csv` / `.json`), **acrescentando a chave `regional_idr`**
derivada no ETL (ver §3). Nenhum campo pessoal (CPF, e-mail individual, telefone,
endereço completo, ID de anexo no Drive) é publicado — coerente com a §6 (LGPD)
de `docs/DADOS-ABERTOS.md` e com o `doGet` da origem, que já filtra esses campos.

**Granularidade:** 1 linha por entidade (chave de origem = CNPJ, publicado apenas
**mascarado**). A localização da linha é o **município da sede** da entidade; a
**área de atuação** (municípios atendidos) é publicada como **contagem** no
agregado de origem — o detalhe município-a-município de atuação fica disponível
para agregação regional via ETL (ver §4, observação sobre `regional_idr`).

---

## 2. Dicionário do dataset `ater/rede-ater` (1 linha por entidade)

Colunas reais expostas pelo agregado público (`EntidadePublica` / `lerAgregadoPublico`),
acrescidas das chaves geográficas derivadas exigidas pelo Observatório.

| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |
|--------|------|---------|-----------|-----------------|-------|-------|
| `cnpj_mascarado` | `texto` | — | CNPJ da entidade com dígitos centrais mascarados (formato `NN.***.***/****-DD`). | Padrão de máscara de `mascararCNPJ()`. | IDR-Paraná — Rede Paranaense de ATER | **PII mitigada:** o CNPJ pleno **nunca** é publicado (LGPD §6). Não usar como chave de join. |
| `razao_social` | `texto` | — | Razão social da entidade prestadora. | Texto livre (3–200 caracteres). | IDR-Paraná — Rede Paranaense de ATER | Dado de pessoa jurídica (não pessoa física); exposto na origem. |
| `nome_fantasia` | `texto` | — | Nome fantasia da entidade. | Texto livre (2–200 caracteres). | IDR-Paraná — Rede Paranaense de ATER | — |
| `tipo_entidade` | `texto` | — | Categoria jurídica/organizacional da entidade. | Enum: `Pública estadual`, `Pública municipal`, `Pública federal`, `Cooperativa`, `Associação`, `Sindicato`, `ONG`, `Empresa privada`, `Outra`. | IDR-Paraná — Rede Paranaense de ATER | Domínio fechado (schema Zod `entidadeSchema.tipo_entidade`). |
| `municipio` | `texto` | — | Município da **sede** da entidade (nome). | Texto livre informado no cadastro. | IDR-Paraná — Rede Paranaense de ATER | Refere-se à sede, não à área de atuação. Não usar como chave de join (acento/grafia divergem). |
| `uf` | `texto` | — | Unidade da Federação da sede (sigla). | Enum de 2 letras (UFs do Brasil); esperado `PR` na maioria. | IDR-Paraná — Rede Paranaense de ATER | Entidades de fora do PR podem aderir; filtrar `uf = "PR"` para recortes estaduais. |
| `cod_ibge` *(inferido)* | `codigo` | — | Código IBGE (7 dígitos) do município da sede. | 399 municípios do PR; FK → `geo/municipios_ref_idr.csv` (`cod_ibge`). | IBGE — Malha Municipal (derivado no ETL) | **(inferido)** Não presente no agregado público da origem para a *sede* (a origem só carrega `codigo_ibge` na aba `area_atuacao`). Derivado no ETL por geocodificação do par `municipio`+`uf` contra o de-para; quando não resolvido, deixar vazio e registrar em `notas`. |
| `regional_idr` *(inferido)* | `codigo` | — | Núcleo Regional do IDR-Paraná da sede (código, zero à esquerda, ex. `"02"`). | 23 regionais; FK → `geo/municipios_ref_idr.csv` (`creg_idr`). | IDR-Paraná (derivado no ETL) | **(inferido)** Chave geográfica canônica do Observatório. Derivada de `cod_ibge` via join com o de-para (ver `docs/GEO.md`). Códigos `01`–`23`, **sem `08`**. Tratar como string. |
| `reg_idr` *(inferido)* | `texto` | — | Nome (sede) do núcleo regional IDR da sede. | 23 rótulos; FK → `geo/municipios_ref_idr.csv` (`reg_idr`). | IDR-Paraná (derivado no ETL) | **(inferido)** Rótulo humano de `regional_idr`. |
| `meso_idr` *(inferido)* | `texto` | — | Mesorregião IDR da sede. | `Norte`, `Metropolitana e Litoral`, `Oeste`, `Noroeste`, `Sudoeste`, `Centro Sul`, `Centro`. | IDR-Paraná (derivado no ETL) | **(inferido)** Nível superior de agregação (não confundir com mesorregiões do IBGE). |
| `area_atuacao` | `inteiro` | nº de municípios | Quantidade de municípios em que a entidade declara atuar. | ≥ 1. | IDR-Paraná — Rede Paranaense de ATER | Contagem agregada (`contarPorCNPJ` sobre a aba `area_atuacao`); a lista nominal de municípios atendidos **não** é publicada por linha. |
| `equipe_total` | `inteiro` | nº de técnicos | Total de profissionais na equipe técnica da entidade. | ≥ 1. | IDR-Paraná — Rede Paranaense de ATER | Contagem agregada (`contarPorCNPJ` sobre a aba `equipe`); **CPFs e nomes da equipe nunca expostos**. |
| `veiculos_total` | `inteiro` | nº de veículos | Soma de veículos declarados (todos os tipos/anos). | ≥ 0. | IDR-Paraná — Rede Paranaense de ATER | Soma de `quantidade` (`somarQuantidade` sobre a aba `veiculos`). |
| `eq_informatica_total` | `inteiro` | nº de itens | Soma de equipamentos de informática declarados. | ≥ 0. | IDR-Paraná — Rede Paranaense de ATER | Soma de `quantidade` sobre a aba `eq_informatica`. |
| `eq_rede_total` | `inteiro` | nº de itens | Soma de equipamentos de rede declarados. | ≥ 0. | IDR-Paraná — Rede Paranaense de ATER | Soma de `quantidade` sobre a aba `eq_rede`. |
| `eq_extensionista_total` | `inteiro` | nº de itens | Soma de equipamentos de uso do extensionista declarados. | ≥ 0. | IDR-Paraná — Rede Paranaense de ATER | Soma de `quantidade` sobre a aba `eq_extensionista`. |
| `imoveis_total` | `inteiro` | nº de imóveis | Total de imóveis declarados pela entidade. | ≥ 0. | IDR-Paraná — Rede Paranaense de ATER | Contagem agregada (`contarPorCNPJ` sobre a aba `imoveis`). |
| `criado_em` | `data` | — | Data de adesão/cadastro da entidade (data do registro na planilha). | ISO `AAAA-MM-DD`. | IDR-Paraná — Rede Paranaense de ATER | Campo `criado_em` gerado pela origem (`datetime`); publicar apenas a **data** (truncar hora). Base da série de adesões (`serieAdesoes`). |
| `status` *(inferido)* | `texto` | — | Situação da entidade no fluxo de aprovação. | `aprovado` \| `pendente_revisao` (entidades `rejeitado` **não** entram no dataset). | IDR-Paraná — Rede Paranaense de ATER | **(inferido)** A origem **filtra** `rejeitado` no `doGet`, mas **não** expõe o campo `status` no agregado. Incluir só se o ETL preservar a distinção aprovado/pendente; caso contrário omitir esta coluna. |

> **Chave de agregação:** como não há identificador público estável (o CNPJ é
> mascarado), o dataset é consumido em **agregados** por `regional_idr`,
> `tipo_entidade` e período (`criado_em`). Para contagens por núcleo regional,
> agregar pelas chaves geográficas derivadas.

---

## 3. Derivação geográfica e a chave `regional_idr` (obrigatória)

Conforme `docs/GEO.md` e `docs/DADOS-ABERTOS.md` §4, **toda** linha de granularidade
municipal deve carregar `cod_ibge` e permitir derivar `regional_idr`:

1. **Sede da entidade:** o agregado de origem traz `municipio` + `uf` (texto), mas
   **não** o `cod_ibge` da sede. O ETL resolve `cod_ibge` por normalização de nome
   (sem acento/caixa) + `uf` contra `assets/data/geo/municipios_ref_idr.csv`,
   e então faz join para obter `creg_idr` (=`regional_idr`), `reg_idr` e `meso_idr`.
   Casos não resolvidos: deixar geo vazio e registrar contagem em `notas` do dataset.
2. **Não duplicar o de-para** dentro do dataset: derivar sempre de
   `geo/municipios_ref_idr.csv` (fonte única). Mudou um vínculo município→regional?
   Atualiza-se só o de-para.
3. **Tratar `creg_idr`/`regional_idr` como string com zero à esquerda** (`"02"`),
   nunca inteiro; códigos `01`–`23`, **sem `08`** (lacuna histórica esperada).

> **Área de atuação por regional (recomendado):** a origem possui, na aba
> `area_atuacao`, o `codigo_ibge` (6–7 dígitos) de **cada** município atendido —
> material ideal para um agregado adicional **contagem de entidades atuantes por
> `regional_idr`**. Hoje esse detalhe **não** é exposto pelo `doGet` (só a
> contagem por entidade). Publicar esse recorte regional exigiria estender o
> agregado público da origem (ou um convênio de dados) — registrar como evolução
> futura, não como dado já disponível.

---

## 4. Notas de proveniência, LGPD e limitações

- **Fonte primária:** IDR-Paraná — Rede Paranaense de ATER (autocadastro de
  entidades). **Órgão responsável:** IDR-Paraná / SEAB. Sistema declarado em
  `eixos.json`: IDR-Paraná (SISATER/GETEC).
- **LGPD (regra dura):** publicar **somente agregados**. Campos da origem
  marcados como PII — `cnpj` pleno, `responsavel_cpf`, `contato2_cpf`, `cpf` da
  equipe, `email`, telefones, endereço completo (`logradouro`/`numero`/`cep`),
  `drive_file_id` de anexos, `ip_hash` do `_log` — **não** são publicados. O CNPJ
  só aparece **mascarado**. Aplicar **supressão de célula** em recortes com poucas
  entidades por `regional_idr` (risco de reidentificação) e registrar a supressão
  em `notas` do `catalog.json`.
- **Dado declaratório e em construção:** os valores são autodeclarados pelas
  entidades no formulário de adesão; a base **cresce continuamente** (cadastro
  aberto). `area_atuacao`/`equipe_total`/`*_total` refletem o que cada entidade
  informou, sem auditoria externa. Cobertura temporal e nº de entidades variam a
  cada carga (`gerado_em` no payload da origem).
- **Município = sede**, não cobertura de atendimento. Análises de cobertura
  territorial de ATER devem usar o recorte de **área de atuação** (ver §3),
  quando disponível, e não o município da sede.
- **Painel irmão do mesmo eixo:** **Relatórios Técnicos de Vistoria (RTV)** —
  `avnergomes/rtv` (Streamlit; KPIs de RTVs, extensão, % entregues, municípios
  atendidos, comparativo por região, mapa). É fonte de um futuro dataset
  `ater/rtv` (a catalogar à parte), também agregável por `regional_idr`.

---

## 5. Fontes inspecionadas (repositório de origem)

Repositório `rededeaterparana/rededeaterparana.github.io`:
- `apps-script/Sheets.gs` — constante `SCHEMA` (todas as abas e colunas) e
  `lerAgregadoPublico()` (subset público exposto).
- `apps-script/Code.gs` — `doGet` (filtra `rejeitado`; cacheia o agregado).
- `painel/src/lib/api.ts` — interface `EntidadePublica` (contrato consumido).
- `painel/src/lib/agregacoes.ts` — agregações do painel (`porChave`, `somaInfra`,
  `serieAdesoes`).
- `form/src/schema/entidade.ts` — schema Zod (tipos, domínios/enums, obrigatoriedade).
- `docs/campos.md` — mapeamento campo → planilha e marcação do que é exposto/PII.

> Campos marcados **(inferido)** acima não constam diretamente do agregado público
> da origem; são derivações do ETL do Observatório (geo) ou campos de fluxo
> internos da origem — não inventados, mas a confirmar na primeira carga real.
