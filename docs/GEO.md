# Backbone Geográfico — Observatório Rural Paranaense

> Plano do backbone geográfico do hub. Fonte da verdade para qualquer pessoa
> (ou agente) que toque em malhas, choropleths ou de-paras territoriais.
> Complementa `docs/PROJETO-BRIEF.md` e a taxonomia de `assets/data/eixos.json`.
> Idioma de conteúdo: **pt-BR**. Toda cor/tipo de mapa via `var(--…)` de
> `assets/css/tokens.css` (nunca hex solto).

---

## 1. Decisão: GeoJSON estático no GitHub Pages + Git LFS

**Decisão travada:** o backbone geográfico do hub é **arquivo estático**
(GeoJSON / TopoJSON / PMTiles) servido pelo próprio GitHub Pages, **versionado e
auditável**, sem servidor de aplicação.

### Por quê (o ponto cego de hoje)
O BDGeo do IDR opera hoje como um **PostgREST local** (banco PostGIS exposto por
API REST na rede interna). Isso é um **ponto cego** para o observatório:

- **Não versionado:** a malha vive num banco; não há histórico Git, diff nem
  revisão de mudança. Não é reprodutível por terceiros.
- **Não público:** depende de rede interna / credencial; um hub em GitHub Pages
  (estático, sem backend) não pode consumir um PostgREST local em produção.
- **Acoplamento a servidor:** introduz disponibilidade, custo e secret de banco
  num projeto cuja premissa é **ser estático** (ver `PROJETO-BRIEF.md`
  — "ETL Python → JSON estático; GitHub Pages").

### O que adotamos no lugar
- **Malhas como dados de borda:** geometrias exportadas uma vez (ETL), commitadas
  como arquivo, servidas por HTTP estático (CDN do Pages).
- **Sem backend em runtime:** o front (HTML/CSS/JS **vanilla**, sem framework)
  faz `fetch()` do arquivo e renderiza no cliente.
- **Pesados via Git LFS:** geometrias grandes (malha municipal ~50 MB, tiles)
  ficam sob **Git LFS** para não inchar o histórico Git de blobs binários.
  O `.gitattributes` na raiz **já está configurado** (ver §5).
- **Reprodutibilidade:** o ETL que gera as malhas é versionado junto; a
  proveniência (fonte, data, ferramenta, tolerância) é documentada aqui e no
  dicionário de dados do painel.

> O PostgREST/BDGeo pode seguir existindo **internamente** como origem de dados
> do ETL, mas **não é dependência de runtime** do hub público.

---

## 2. Hierarquia territorial e a chave única `regional_idr`

A taxonomia geográfica do observatório é a **regionalização administrativa do
IDR-Paraná** — a mesma de `eixos.json` (`geo.niveis`,
`geo.chave = "regional_idr"`). A chave de junção entre **qualquer painel** e a
geometria é sempre `regional_idr`.

```
Estado (1)
  └─ Mesorregião IDR (7)
       └─ Regional / Núcleo Regional IDR (23)   ← chave: regional_idr
            └─ Município (399)                    ← chave IBGE: cod_ibge
```

| Nível         | Quantidade | Chave de junção                       |
|---------------|------------|---------------------------------------|
| Estado        | 1          | `PR` (UF 41)                          |
| Mesorregião   | 7          | `meso_idr` (texto)                    |
| **Regional**  | **23**     | **`regional_idr`** (núcleo regional)  |
| Município     | 399        | `cod_ibge` (7 dígitos)                |

> As 7 mesorregiões IDR são: **Norte, Metropolitana e Litoral, Oeste, Noroeste,
> Sudoeste, Centro Sul, Centro** (são a regionalização do IDR, **não** as
> mesorregiões do IBGE — não confundir nem misturar fontes).

### Arquivos de referência já presentes no repo

#### `assets/data/geo/municipios_ref_idr.csv` — o de-para canônico
Tabela de equivalência 399 municípios → regional → mesorregião. Colunas:

| Coluna      | Tipo   | Descrição                                              | Exemplo               |
|-------------|--------|--------------------------------------------------------|-----------------------|
| `cod_ibge`  | int(7) | Código IBGE do município (chave primária)              | `4100103`             |
| `municipio` | texto  | Nome oficial do município (com acento)                 | `Abatiá`              |
| `creg_idr`  | texto  | **Código** do núcleo regional, com zero à esquerda     | `13`, `02`            |
| `reg_idr`   | texto  | **Nome** do núcleo regional (sede)                     | `Cornélio Procópio`   |
| `meso_idr`  | texto  | Mesorregião IDR                                         | `Norte`               |

> **`regional_idr` = `creg_idr`** (código) na junção; `reg_idr` é o rótulo
> humano. Os códigos vão de `01` a `23` e **não há `08`** (lacuna histórica na
> numeração dos núcleos — esperado, não é erro). Sempre trate `creg_idr` como
> **string com zero à esquerda** (ex.: `"02"`), nunca como inteiro, para casar
> com o `cod` do mapa SVG e evitar perda do zero.

#### `assets/data/geo/pr_nucleos_regionais.json` — o mapa SVG por 23 núcleos
Mapa vetorial leve (≈128 KB) do PR dividido nos **23 núcleos regionais**, pronto
para choropleth em SVG sem dependências. Estrutura **real** do arquivo:

```jsonc
{
  "w": 920,        // largura do viewBox (use em <svg viewBox="0 0 w h">)
  "h": 648.7,      // altura do viewBox
  "n": 23,         // nº de núcleos (sanity check)
  "nucleos": [
    {
      "nome": "Apucarana",    // rótulo humano do núcleo (sede)
      "key":  "APUCARANA",    // chave em CAIXA ALTA, sem acento
      "cod":  20,             // código do núcleo (numérico) → casa com creg_idr
      "d":    "M422.1,210.2 L421.4,211.1 …",  // path SVG (atributo d)
      "cx":   433.6,          // centróide X (posicionar rótulo)
      "cy":   175.2           // centróide Y
    }
    // … 23 núcleos
  ]
}
```

> **Junção com a tabela:** `cod` (numérico, ex.: `20`) ↔ `creg_idr` (string com
> zero, ex.: `"20"`). Normalize com zero-pad de 2 dígitos antes de comparar:
> `String(n.cod).padStart(2, "0") === row.creg_idr`. A coordenada de junção
> "oficial" do projeto continua sendo **`regional_idr`** — `cod`/`creg_idr` são a
> sua materialização nos dois arquivos.

---

## 3. Plano da malha municipal `mun_PR.json` (~50 MB)

Para choropleths **por município** (399 polígonos) precisamos da malha municipal
detalhada. O arquivo bruto pesa ~50 MB — inviável servir cru no front. Pipeline:

### Passo 0 — Obter a fonte
- **Origem preferencial:** núcleo `c2-parana` (`avnergomes/c2-parana`) ou a base
  `cibiogas` (ambas já trazem a malha municipal do PR; ver `eixos.json`
  — núcleo de inteligência e eixo Infraestrutura/Energia).
- **Alternativa pública:** malha municipal do IBGE (recorte UF 41 — Paraná).
- Registre **proveniência** (fonte, ano da malha, data de extração, sistema de
  referência) no dicionário de dados do backbone.

### Passo 1 — Padronizar atributos (CRS e chaves)
- Garantir **CRS WGS84 / EPSG:4326** (lat/long) para uso web.
- Manter **apenas** os atributos necessários por feature:
  `cod_ibge` (7 dígitos, string), `municipio`, `creg_idr`, `meso_idr` —
  derivados de `municipios_ref_idr.csv` via *join* por `cod_ibge`.
  Descartar atributos supérfluos do shapefile original (reduz tamanho).

### Passo 2 — Simplificar preservando topologia
Usar **mapshaper** (ou `topojson`) com simplificação **que preserve a topologia**
(fronteiras compartilhadas não se descolam nem geram vãos/sobreposições):

```bash
# Simplificação topológica (Visvalingam), preservando bordas compartilhadas.
# Ajustar a tolerância (%) ao alvo de tamanho/legibilidade do mapa.
mapshaper mun_PR_bruto.shp \
  -simplify 8% keep-shapes \
  -clean \
  -o format=geojson precision=0.0001 mun_PR.geojson
```

- **`keep-shapes`**: não deixa polígono pequeno colapsar e sumir.
- **`-clean`**: corrige gaps/overlaps após simplificar.
- **`precision`**: corta casas decimais redundantes (ganho de tamanho grande).
- **Tolerância:** começar em ~5–10% e iterar; alvo de **versão web ≤ ~2–3 MB**
  para a malha municipal simplificada. Validar visualmente no zoom estadual.

### Passo 3 — Converter para TopoJSON e/ou tiles
- **TopoJSON** (`mun_PR.topojson`): codifica arcos compartilhados **uma vez** —
  tipicamente **80%+ menor** que o GeoJSON equivalente. Ideal para o front
  reconstruir polígonos no cliente (lib `topojson-client`).
- **PMTiles** (`mun_PR.pmtiles`): para zoom/pan fluido e *level-of-detail*, gerar
  tiles vetoriais num único arquivo (via `tippecanoe` → `.mbtiles` →
  `pmtiles convert`). Servível estático no Pages, consumido por MapLibre GL.
  Usar **somente** quando o painel exigir mapa interativo com zoom; para
  choropleth estático, TopoJSON basta.

```bash
# GeoJSON simplificado → TopoJSON (quantizado)
mapshaper mun_PR.geojson -o format=topojson quantization=1e5 mun_PR.topojson

# (opcional) GeoJSON → tiles vetoriais → PMTiles
tippecanoe -zg --drop-densest-as-needed -o mun_PR.mbtiles mun_PR.geojson
pmtiles convert mun_PR.mbtiles mun_PR.pmtiles
```

### Passo 4 — Versionar e servir
- **Bruto (~50 MB)** e derivados pesados (`.topojson`, `.pmtiles`): **Git LFS**
  (padrões já no `.gitattributes`; ver §5). Não commitar binário grande direto.
- **Versão web simplificada** (`mun_PR.topojson` ≤ ~2–3 MB): é a que o front
  consome por `fetch()`. Documentar no dicionário de dados.
- **Nomenclatura:** prefixo `mun_` aciona a regra LFS
  (`assets/data/geo/mun_*.json filter=lfs …`). Mantenha as malhas em
  `assets/data/geo/`.

### Resumo dos artefatos da malha municipal
| Artefato                 | Origem            | Tamanho alvo | Versionamento | Uso                          |
|--------------------------|-------------------|--------------|---------------|------------------------------|
| `mun_PR_bruto.*`         | c2-parana/IBGE    | ~50 MB       | Git LFS       | insumo do ETL (não servir)   |
| `mun_PR.topojson`        | mapshaper -simplify | ≤ ~2–3 MB  | Git LFS       | choropleth municipal no front|
| `mun_PR.pmtiles`         | tippecanoe/pmtiles | variável    | Git LFS       | mapa interativo c/ zoom (opt)|
| `pr_nucleos_regionais.json` | já presente    | ~128 KB      | Git normal    | choropleth por 23 núcleos    |
| `municipios_ref_idr.csv` | já presente       | ~18 KB       | Git normal    | de-para / join de atributos  |

---

## 4. Convenção: uma malha, todos os painéis (`regional_idr`)

**Regra do hub:** todo painel **referencia a chave `regional_idr`** e **reusa UMA
única cópia** de cada malha. **Proibido duplicar** os ~50 MB (ou a malha web) em
cada repo de painel.

- **Junção sempre por chave, nunca por nome:** painéis casam seus dados à
  geometria por `regional_idr` (`creg_idr`) ou `cod_ibge` — **nunca** por nome de
  município/região (acento, grafia e maiúsculas divergem entre fontes).
- **Fonte canônica única:** as malhas vivem **só** em
  `observatorio-rural-parana.github.io/assets/data/geo/`. Painéis externos do
  ecossistema `avnergomes` (ver `PROJETO-BRIEF.md`) consomem essa cópia por URL
  estável do hub, **não** carregam a própria.
- **Eliminar duplicatas existentes:** repos que hoje carregam sua própria malha
  de ~50 MB devem **remover** o arquivo e apontar para a cópia única do hub
  (reduz pegada do ecossistema e garante que todos vejam a mesma fronteira).
- **De-para central:** qualquer agregação município → regional → mesorregião usa
  `municipios_ref_idr.csv` como **único** dicionário; não recriar mapeamentos
  paralelos por painel.
- **Versionamento de geometria:** ao atualizar uma malha, versionar **uma vez**
  no hub; todos os painéis herdam a mudança via a URL compartilhada.

---

## 5. Checklist de setup do Git LFS (ANTES de adicionar a malha)

> Faça **na ordem**. Adicionar a malha de ~50 MB **sem** o LFS instalado e
> rastreando incha o histórico Git de forma irreversível (precisaria reescrever
> histórico). O `.gitattributes` já está versionado; falta o lado local.

- [ ] **1. Instalar o cliente Git LFS** na máquina
      (`git lfs version` deve responder; se não, instalar via gerenciador da
      plataforma).
- [ ] **2. Habilitar os hooks do LFS no repo** uma vez:
      `git lfs install`
- [ ] **3. Confirmar os padrões já rastreados** (vêm do `.gitattributes`):
      `git lfs track`
      Deve listar: `assets/data/geo/mun_*.json`, `*.geojson`, `*.topojson`,
      `*.pmtiles`, `*.fgb`.
- [ ] **4. (Se faltar algum padrão)** adicioná-lo e commitar o `.gitattributes`:
      `git lfs track "assets/data/geo/mun_*.json"`
- [ ] **5. Garantir que o `.gitattributes` está commitado ANTES** de adicionar
      qualquer arquivo grande (o filtro precisa existir no momento do `git add`).
- [ ] **6. Só então** adicionar a malha:
      `git add assets/data/geo/mun_PR.topojson`
- [ ] **7. Verificar que entrou no LFS** (e não como blob normal):
      `git lfs status` e `git lfs ls-files` devem listar o arquivo.
- [ ] **8. Conferir cota do GitHub Pages/LFS** (limites de armazenamento e banda
      do LFS) e o **limite de 100 MB por arquivo** do GitHub — manter a versão
      web bem abaixo disso (alvo ≤ ~2–3 MB).
- [ ] **9. Push** e, no clone limpo de CI, confirmar `git lfs pull` traz os
      ponteiros corretamente.

> **Regra prática:** se `git lfs ls-files` **não** mostra o arquivo após o commit,
> ele entrou como blob normal — desfaça (`git reset`) e refaça após `git lfs install`.

---

## 6. Como usar `pr_nucleos_regionais.json` (choropleth SVG por núcleo)

Mapa coroplético dos **23 núcleos regionais** sem libs de mapa — só SVG +
`fetch()`. Cores **sempre** via tokens (`var(--green-l)` … `var(--green-d)` para
escala sequencial; `var(--azul-l)`/`var(--azul-d)` para escalas alternativas).

### 6.1 Estrutura consumida
- `w`, `h` → `viewBox="0 0 w h"` do `<svg>`.
- `nucleos[]` → cada item vira um `<path d="…">`.
- `cx`, `cy` → posição do rótulo (`<text>`) de cada núcleo.
- `cod` (numérico) → junta com seu dado por `regional_idr`/`creg_idr`
  (zero-pad 2 dígitos).

### 6.2 Esqueleto de renderização (JS vanilla, acessível)

```html
<figure>
  <figcaption id="mapa-titulo">Indicador X por núcleo regional IDR — Paraná</figcaption>
  <svg id="mapa-pr" role="img" aria-labelledby="mapa-titulo" xmlns="http://www.w3.org/2000/svg"></svg>
</figure>
```

```js
// valores por regional_idr (creg_idr como string com zero à esquerda)
const dados = { "20": 132.5, "12": 88.0 /* … */ };

const escalaCor = (v) => {
  // 5 faixas usando APENAS tokens do design system (tokens.css)
  if (v == null)  return "var(--gray-l)";          // sem dado
  if (v < 50)     return "var(--green-l)";
  if (v < 100)    return "var(--olive-l)";
  if (v < 150)    return "var(--olive)";
  if (v < 200)    return "var(--green)";
  return "var(--green-d)";
};

const res = await fetch("./assets/data/geo/pr_nucleos_regionais.json");
if (!res.ok) throw new Error(`Falha ao carregar malha: ${res.status}`); // fail fast
const malha = await res.json();
if (!Array.isArray(malha.nucleos) || malha.nucleos.length !== malha.n) {
  throw new Error("Malha de núcleos inválida ou incompleta.");          // valida borda
}

const svg = document.getElementById("mapa-pr");
const SVGNS = "http://www.w3.org/2000/svg";
svg.setAttribute("viewBox", `0 0 ${malha.w} ${malha.h}`);

for (const nuc of malha.nucleos) {
  const chave = String(nuc.cod).padStart(2, "0");   // 20 → "20", casa com creg_idr
  const valor = dados[chave] ?? null;

  const path = document.createElementNS(SVGNS, "path");
  path.setAttribute("d", nuc.d);
  path.setAttribute("fill", escalaCor(valor));
  path.setAttribute("stroke", "var(--paper)");      // fronteiras = cor do papel
  path.setAttribute("stroke-width", "1");
  path.setAttribute("tabindex", "0");               // foco por teclado
  path.setAttribute("role", "img");
  path.setAttribute("aria-label",
    `${nuc.nome}: ${valor == null ? "sem dado" : valor}`);
  svg.appendChild(path);

  // rótulo opcional no centróide
  const txt = document.createElementNS(SVGNS, "text");
  txt.setAttribute("x", nuc.cx);
  txt.setAttribute("y", nuc.cy);
  txt.setAttribute("text-anchor", "middle");
  txt.setAttribute("font-size", "10");
  txt.setAttribute("fill", "var(--ink)");
  txt.setAttribute("aria-hidden", "true");          // já descrito no aria-label do path
  txt.textContent = nuc.nome;
  svg.appendChild(txt);
}
```

### 6.3 Acessibilidade (WCAG AA) — obrigatório
- `<svg role="img" aria-labelledby>` com `<figcaption>` descrevendo o mapa.
- Cada `<path>` com `aria-label` (nome do núcleo + valor) e `tabindex="0"` para
  navegação por teclado; **foco visível** via `--focus-ring`
  (`:focus-visible { outline: 2px solid var(--focus-ring); }`).
- **Não usar cor como único canal:** acompanhar o mapa de uma **legenda** e/ou
  **tabela de dados** equivalente (texto) — leitura por terceiros e leitores de
  tela.
- Garantir **contraste AA** entre fill e stroke; stroke em `var(--paper)` separa
  os núcleos sem depender de matiz.
- Respeitar `@media (prefers-reduced-motion)` se houver transição de hover.

### 6.4 Notas
- Para **choropleth municipal** (399), repetir o padrão com `mun_PR.topojson`
  (reconstruir paths com `topojson-client` e juntar por `cod_ibge`); a escala de
  cores e as regras de acessibilidade são as mesmas.
- **Nunca hardcodar a lista de núcleos** no HTML — sempre derivar de
  `pr_nucleos_regionais.json` (e os painéis, de `eixos.json`), conforme as
  convenções de autoria do `PROJETO-BRIEF.md`.

---

## Referências internas
- `docs/PROJETO-BRIEF.md` — decisões travadas, convenções de autoria.
- `assets/data/eixos.json` — taxonomia (`geo.chave = "regional_idr"`).
- `assets/css/tokens.css` — design system (cores/tipografia do mapa).
- `assets/data/geo/municipios_ref_idr.csv` — de-para canônico.
- `assets/data/geo/pr_nucleos_regionais.json` — mapa SVG dos 23 núcleos.
- `.gitattributes` (raiz) — regras de Git LFS para malhas/tiles.
