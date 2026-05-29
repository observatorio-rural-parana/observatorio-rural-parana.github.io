"""export_open_data.py — Etapa 3 do pipeline de um painel temático.

Observatório Rural Paranaense — cookiecutter de painel.
Ordem do pipeline:  ingest  ->  model  ->  export_open_data  ->  (report)

RESPONSABILIDADE DESTA ETAPA
----------------------------
Emitir o CONTRATO DE DADOS ABERTOS para um dataset (ver docs/DADOS-ABERTOS.md):
  1) {dataset}.csv   — formato CANÔNICO (UTF-8 SEM BOM, separador ",", decimal ".");
  2) {dataset}.json  — espelho para consumo web (gerado a partir do mesmo df);
  3) {dataset}.dict.json + DICIONARIO.md — dicionário (máquina + humano);
  4) entrada (upsert) em assets/data/catalog.json — manifesto único do portal.

Regras duras:
  - SÓ AGREGADOS; nunca CPF/CNPJ (já garantido em model.aplicar_supressao_lgpd,
    revalidado aqui por segurança — defesa em profundidade).
  - `regional_idr` sempre presente como chave (direta ou derivável de cod_ibge).
  - Atribuição obrigatória: `fonte` e `orgao`.
  - IDEMPOTENTE: reescreve os arquivos do dataset e faz upsert no catálogo por
    `id`. Rodar duas vezes com a mesma entrada produz o mesmo resultado.

Convenções de catálogo: docs/DADOS-ABERTOS.md §2.2 (campos obrigatórios).

Uso:
    python -m pipeline.export_open_data
"""

from __future__ import annotations

import hashlib
import io
import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import model

# ---------------------------------------------------------------------------
# Caminhos canônicos no hub. Os dados abertos vivem sob assets/data/{eixo}/;
# o catálogo é único em assets/data/catalog.json.
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "assets" / "data"
CATALOG_PATH = DATA_DIR / "catalog.json"

# Licença padrão do portal (docs/DADOS-ABERTOS.md §1, P3).
LICENCA_PADRAO = {
    "id": "CC-BY-4.0",
    "nome": "Creative Commons Atribuição 4.0 Internacional",
    "url": "https://creativecommons.org/licenses/by/4.0/deed.pt-br",
}

# Níveis geográficos válidos (cobertura_geografica.nivel).
NIVEIS_GEO = ("estado", "mesorregiao", "regional_idr", "municipio")

# Tipos canônicos de coluna (docs/DADOS-ABERTOS.md §3.1).
TIPOS_DICIONARIO = ("inteiro", "decimal", "texto", "data", "ano", "booleano", "codigo")


@dataclass(frozen=True)
class Coluna:
    """Uma linha do dicionário de dados (humano + máquina)."""

    coluna: str
    tipo: str            # um de TIPOS_DICIONARIO
    unidade: str         # "R$", "ha", "t", "%", "—"
    descricao: str
    dominio: str         # valores válidos / faixa / enum / FK
    fonte: str
    notas: str = ""


@dataclass(frozen=True)
class DatasetSpec:
    """Metadados de UM dataset publicado (alimenta dicionário e catálogo).

    TODO: preencher com os valores REAIS do painel. Os campos espelham os
    obrigatórios do catalog.json (docs/DADOS-ABERTOS.md §2.2).
    """

    eixo: str                       # FK -> eixos.json (eixos[].id). NÃO inventar.
    dataset: str                    # kebab-case estável (ex.: "vbp-municipios")
    titulo: str
    descricao: str                  # 1-3 frases
    fonte: str                      # origem primária
    orgao: str                      # instituição responsável
    periodicidade: str              # anual|mensal|diaria|semanal|eventual|unica
    ultima_atualizacao: str         # ISO AAAA-MM-DD
    cobertura_temporal: dict        # {"inicio": "AAAA", "fim": "AAAA"}
    nivel_geografico: str           # um de NIVEIS_GEO
    unidades_geograficas: int       # ex.: 399 municípios, 23 regionais
    versao: str                     # SemVer reduzido "MAJOR.MINOR"
    colunas: tuple[Coluna, ...]     # dicionário (toda coluna documentada)
    formatos: tuple[str, ...] = ("csv", "json")  # csv sempre presente
    painel: dict | None = None      # {"nome","url"} (opcional)
    notas: str = ""                 # limitações, ressalvas LGPD/supressão
    licenca: dict = field(default_factory=lambda: dict(LICENCA_PADRAO))

    @property
    def id(self) -> str:
        return f"{self.eixo}/{self.dataset}"

    @property
    def dir(self) -> Path:
        return DATA_DIR / self.eixo


# ---------------------------------------------------------------------------
# Validações de boundary
# ---------------------------------------------------------------------------

COLUNAS_PROIBIDAS = {"cpf", "cnpj", "nit", "caf", "nome_produtor", "inscricao_estadual"}


def _validar_spec(spec: DatasetSpec) -> None:
    if spec.nivel_geografico not in NIVEIS_GEO:
        raise ValueError(f"nivel_geografico inválido: {spec.nivel_geografico!r}")
    if "csv" not in spec.formatos:
        raise ValueError("`csv` deve sempre estar em formatos (formato canônico).")
    for col in spec.colunas:
        if col.tipo not in TIPOS_DICIONARIO:
            raise ValueError(f"Tipo inválido na coluna {col.coluna!r}: {col.tipo!r}")
    if not spec.fonte or not spec.orgao:
        raise ValueError("Atribuição obrigatória: `fonte` e `orgao` não podem ser vazios.")


def _validar_df(df: pd.DataFrame, spec: DatasetSpec) -> None:
    # LGPD: defesa em profundidade — nada de identificadores pessoais.
    presentes = COLUNAS_PROIBIDAS & {c.lower() for c in df.columns}
    if presentes:
        raise ValueError(f"Colunas identificáveis no df (LGPD): {sorted(presentes)}")

    # `regional_idr` deve existir OU ser derivável de cod_ibge.
    if "regional_idr" not in df.columns and "cod_ibge" not in df.columns:
        raise ValueError(
            "Dataset sem `regional_idr` nem `cod_ibge`: a chave geográfica "
            "canônica precisa estar presente ou ser derivável (docs/GEO.md §4)."
        )

    # Dicionário deve cobrir exatamente as colunas do df.
    cols_df = list(df.columns)
    cols_dict = [c.coluna for c in spec.colunas]
    if set(cols_df) != set(cols_dict):
        faltam = set(cols_df) - set(cols_dict)
        sobram = set(cols_dict) - set(cols_df)
        raise ValueError(
            "Dicionário não casa com as colunas do dataset. "
            f"Sem dicionário: {sorted(faltam)}; sem dado: {sorted(sobram)}."
        )


# ---------------------------------------------------------------------------
# Escrita dos artefatos
# ---------------------------------------------------------------------------

def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def escrever_csv(df: pd.DataFrame, destino: Path) -> tuple[int, str]:
    """CSV canônico: UTF-8 SEM BOM, separador ',', decimal '.', sem índice.

    Devolve (bytes, sha256). Idempotente: mesma entrada -> mesmo arquivo.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    df.to_csv(buf, index=False, sep=",", decimal=".", lineterminator="\n")
    data = buf.getvalue().encode("utf-8")  # 'utf-8' (não 'utf-8-sig') => sem BOM
    destino.write_bytes(data)
    return len(data), _sha256_bytes(data)


def escrever_json(df: pd.DataFrame, destino: Path) -> tuple[int, str]:
    """Espelho JSON (array de objetos) para consumo web. Devolve (bytes, sha256)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    registros = df.to_dict(orient="records")
    data = json.dumps(registros, ensure_ascii=False, indent=2).encode("utf-8")
    destino.write_bytes(data)
    return len(data), _sha256_bytes(data)


def escrever_dicionario(spec: DatasetSpec) -> Path:
    """Gera {dataset}.dict.json (máquina) e DICIONARIO.md (humano). Idempotente."""
    # ---- máquina: {dataset}.dict.json -------------------------------------
    dict_json = {
        "dataset": spec.id,
        "titulo": f"Dicionário — {spec.titulo}",
        "versao": spec.versao,
        "colunas": [
            {
                "coluna": c.coluna,
                "tipo": c.tipo,
                "unidade": c.unidade,
                "descricao": c.descricao,
                "dominio": c.dominio,
                "fonte": c.fonte,
                "notas": c.notas,
            }
            for c in spec.colunas
        ],
    }
    dict_path = spec.dir / f"{spec.dataset}.dict.json"
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    dict_path.write_text(
        json.dumps(dict_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # ---- humano: DICIONARIO.md (tabela markdown) --------------------------
    linhas = [
        f"# Dicionário de dados — {spec.titulo}",
        "",
        f"- **Dataset:** `{spec.id}`",
        f"- **Versão:** {spec.versao}",
        f"- **Fonte:** {spec.fonte}",
        f"- **Órgão:** {spec.orgao}",
        f"- **Última atualização:** {spec.ultima_atualizacao}",
        "",
        "| coluna | tipo | unidade | descrição | domínio/valores | fonte | notas |",
        "|--------|------|---------|-----------|-----------------|-------|-------|",
    ]
    for c in spec.colunas:
        linhas.append(
            f"| `{c.coluna}` | `{c.tipo}` | {c.unidade or '—'} | {c.descricao} | "
            f"{c.dominio} | {c.fonte} | {c.notas or '—'} |"
        )
    linhas.append("")
    md_path = spec.dir / "DICIONARIO.md"
    md_path.write_text("\n".join(linhas), encoding="utf-8")
    return dict_path


def _entrada_catalogo(spec: DatasetSpec, arquivos: list[dict]) -> dict:
    """Monta a entrada do dataset no catalog.json (docs/DADOS-ABERTOS.md §2.2)."""
    entrada = {
        "id": spec.id,
        "titulo": spec.titulo,
        "eixo": spec.eixo,
        "descricao": spec.descricao,
        "fonte": spec.fonte,
        "orgao": spec.orgao,
        "periodicidade": spec.periodicidade,
        "ultima_atualizacao": spec.ultima_atualizacao,
        "cobertura_temporal": spec.cobertura_temporal,
        "cobertura_geografica": {
            "nivel": spec.nivel_geografico,
            "unidades": spec.unidades_geograficas,
        },
        "formatos": list(spec.formatos),
        "arquivos": arquivos,
        "licenca": spec.licenca,
        "dicionario": f"/assets/data/{spec.eixo}/{spec.dataset}.dict.json",
        "versao": spec.versao,
    }
    if spec.painel:
        entrada["painel"] = spec.painel
    if spec.notas:
        entrada["notas"] = spec.notas
    return entrada


def atualizar_catalogo(entrada: dict) -> None:
    """Upsert da entrada no catalog.json por `id`. Idempotente; preserva o resto."""
    if CATALOG_PATH.exists():
        catalogo = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    else:
        # Esqueleto inicial (docs/DADOS-ABERTOS.md §2.2).
        catalogo = {
            "$schema": "./catalog.schema.json",
            "portal": "Observatório Rural Paranaense",
            "licenca_padrao": dict(LICENCA_PADRAO),
            "gerado_em": entrada["ultima_atualizacao"],
            "datasets": [],
        }

    datasets = catalogo.setdefault("datasets", [])
    # Upsert por id (substitui in-place se já existe; senão anexa).
    idx = next((i for i, d in enumerate(datasets) if d.get("id") == entrada["id"]), None)
    if idx is None:
        datasets.append(entrada)
    else:
        datasets[idx] = entrada

    # Ordena por id para diffs estáveis (idempotência do arquivo).
    datasets.sort(key=lambda d: d.get("id", ""))
    catalogo["gerado_em"] = entrada["ultima_atualizacao"]

    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def exportar(df: pd.DataFrame, spec: DatasetSpec) -> dict:
    """Emite todo o contrato de dados abertos para `spec`. Idempotente.

    Devolve a entrada de catálogo escrita (útil para testes/relatório).
    """
    _validar_spec(spec)
    _validar_df(df, spec)

    arquivos: list[dict] = []

    csv_path = spec.dir / f"{spec.dataset}.csv"
    nbytes, digest = escrever_csv(df, csv_path)
    arquivos.append(
        {
            "formato": "csv",
            "url": f"/assets/data/{spec.eixo}/{spec.dataset}.csv",
            "bytes": nbytes,
            "sha256": digest,
        }
    )

    if "json" in spec.formatos:
        json_path = spec.dir / f"{spec.dataset}.json"
        nbytes, digest = escrever_json(df, json_path)
        arquivos.append(
            {
                "formato": "json",
                "url": f"/assets/data/{spec.eixo}/{spec.dataset}.json",
                "bytes": nbytes,
                "sha256": digest,
            }
        )

    # XLSX é opcional e gerado a partir do CSV (nunca a fonte primária).
    # TODO (opcional): implementar com df.to_excel(... engine="openpyxl") se
    #       "xlsx" estiver em spec.formatos.

    escrever_dicionario(spec)
    entrada = _entrada_catalogo(spec, arquivos)
    atualizar_catalogo(entrada)

    print(
        f"[export] {spec.id}: {len(df)} linhas -> "
        f"{', '.join(a['formato'] for a in arquivos)} + dicionário + catálogo."
    )
    return entrada


# ---------------------------------------------------------------------------
# Especificação do dataset deste painel.
# TODO: preencher com base nas COLUNAS REAIS do df produzido por model.py.
#       Marque campos inferidos com "(inferido)" e não invente dados.
# ---------------------------------------------------------------------------

SPEC = DatasetSpec(
    eixo="TODO-eixo-de-eixos.json",        # ex.: "desempenho-economico"
    dataset="TODO-dataset",                # ex.: "vbp-municipios"
    titulo="TODO — título legível em pt-BR",
    descricao="TODO — o que o dataset contém (1 a 3 frases).",
    fonte="TODO — origem primária (ex.: DERAL/SEAB — VBP)",
    orgao="TODO — instituição (ex.: IDR-Paraná / SEAB)",
    periodicidade="anual",                 # anual|mensal|diaria|semanal|eventual|unica
    ultima_atualizacao="AAAA-MM-DD",       # ISO 8601
    cobertura_temporal={"inicio": "AAAA", "fim": "AAAA"},
    nivel_geografico="municipio",          # estado|mesorregiao|regional_idr|municipio
    unidades_geograficas=399,
    versao="1.0",
    colunas=(
        # TODO: uma Coluna por coluna REAL do dataset. Exemplo abaixo (ajuste):
        # Coluna("cod_ibge", "codigo", "—", "Código IBGE do município (7 díg.).",
        #        "399 municípios; FK -> geo/municipios_ref_idr.csv (cod_ibge).",
        #        "IBGE — Malha Municipal", "Chave primária."),
        # Coluna("regional_idr", "codigo", "—", "Núcleo Regional do IDR-Paraná.",
        #        "23 regionais; FK -> geo/municipios_ref_idr.csv (creg_idr).",
        #        "IDR-Paraná", "Derivado de cod_ibge no ETL."),
    ),
    painel=None,                           # {"nome": "...", "url": "..."}
    notas="",
)


def main() -> None:
    df = model.main()
    exportar(df, SPEC)


if __name__ == "__main__":
    main()
