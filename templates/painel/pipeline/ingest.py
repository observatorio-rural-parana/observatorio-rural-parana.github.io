"""ingest.py — Etapa 1 do pipeline de um painel temático.

Observatório Rural Paranaense — cookiecutter de painel.
Ordem do pipeline:  ingest  ->  model  ->  export_open_data  ->  (report)

RESPONSABILIDADE DESTA ETAPA
----------------------------
Baixar/ler a FONTE BRUTA e materializá-la sem transformação semântica.
Aqui NÃO mora regra de negócio: nada de join, agregação, normalização de
`regional_idr` ou supressão LGPD — isso é responsabilidade de `model.py`.

O que esta etapa PODE fazer:
  - baixar de uma URL/API ou ler um arquivo local (CSV/XLSX/JSON/planilha SEAB-IDR);
  - validar minimamente o "boundary" (a fonte respondeu? o arquivo existe?
    tem as colunas esperadas?) e FALHAR RÁPIDO com mensagem clara;
  - persistir uma cópia BRUTA imutável em `data/raw/` para reprodutibilidade.

O que esta etapa NÃO faz:
  - limpar/renomear colunas com semântica de negócio;
  - calcular indicadores, juntar com o de-para geográfico, agregar;
  - qualquer decisão LGPD (a anonimização/agregação ocorre em `model.py`).

Convenções (ver docs/DADOS-ABERTOS.md e docs/PROJETO-BRIEF.md):
  - Idioma de conteúdo: pt-BR.  Atribuição de fonte sempre explícita.
  - Dependências sóbrias: `pandas` basta; evitar libs exóticas.
  - Idempotente: rodar duas vezes com a mesma fonte produz o mesmo `data/raw/`.

Uso:
    python -m pipeline.ingest
    # ou
    python pipeline/ingest.py
"""

from __future__ import annotations

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuração da fonte bruta.
# TODO: preencher para o painel concreto. Mantenha tudo aqui (sem hardcode
#       espalhado). NUNCA coloque segredos/tokens em código — use variáveis de
#       ambiente quando a fonte exigir credencial (ver docs/DADOS-ABERTOS.md §5).
# ---------------------------------------------------------------------------

# Raiz do repositório (este arquivo fica em <repo>/pipeline/ingest.py).
REPO_ROOT = Path(__file__).resolve().parents[1]

# Onde guardar a cópia bruta imutável da fonte (insumo do model.py).
RAW_DIR = REPO_ROOT / "data" / "raw"


@dataclass(frozen=True)
class FonteBruta:
    """Descreve UMA fonte bruta a ingerir (imutável)."""

    # Identificador estável do bruto (kebab-case), vira nome do arquivo em data/raw/.
    nome: str
    # URL de download OU None se a fonte é um arquivo local já presente no repo.
    url: str | None
    # Caminho local de origem (quando a fonte não é baixada por HTTP).
    caminho_local: Path | None
    # Extensão/formato do bruto: "csv" | "xlsx" | "json".
    formato: str
    # Atribuição (obrigatória no contrato): origem primária e instituição.
    fonte: str   # ex.: "DERAL/SEAB — Valor Bruto da Produção"
    orgao: str   # ex.: "IDR-Paraná / SEAB"


# TODO: declarar a(s) fonte(s) reais do painel.
FONTES: tuple[FonteBruta, ...] = (
    # Exemplo (ajuste/remova):
    # FonteBruta(
    #     nome="vbp-bruto",
    #     url="https://exemplo.seab.pr.gov.br/vbp.csv",
    #     caminho_local=None,
    #     formato="csv",
    #     fonte="DERAL/SEAB — Valor Bruto da Produção Agropecuária",
    #     orgao="IDR-Paraná / SEAB",
    # ),
)


def _baixar(url: str, destino: Path) -> None:
    """Baixa `url` para `destino`. Falha rápido em erro de rede/HTTP.

    Idempotente o suficiente: sempre sobrescreve o destino com o conteúdo atual
    da fonte. Para snapshots imutáveis por versão, ver export_open_data/_versions.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        # urllib (stdlib) evita dependência extra. Para APIs autenticadas,
        # injetar headers/credenciais via variáveis de ambiente (nunca no código).
        with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status} ao baixar {url}")
            destino.write_bytes(resp.read())
    except Exception as exc:  # boundary: traduz erro técnico em mensagem clara
        raise RuntimeError(f"Falha ao baixar a fonte bruta de {url}: {exc}") from exc


def _ler_bruto(destino: Path, formato: str) -> pd.DataFrame:
    """Lê o arquivo bruto como DataFrame, sem aplicar semântica de negócio.

    Mantemos `dtype=str` por padrão na leitura de CSV para PRESERVAR códigos com
    zero à esquerda (ex.: `creg_idr` = "02"). A tipagem semântica é feita em
    `model.py`, não aqui.
    """
    if not destino.exists():
        raise FileNotFoundError(f"Arquivo bruto ausente: {destino}")

    if formato == "csv":
        return pd.read_csv(destino, dtype=str, keep_default_na=False)
    if formato == "xlsx":
        # openpyxl é a engine padrão do pandas para .xlsx (dependência comum).
        return pd.read_excel(destino, dtype=str)
    if formato == "json":
        return pd.read_json(destino, dtype=False)
    raise ValueError(f"Formato de fonte não suportado: {formato!r}")


def _sha256(caminho: Path) -> str:
    """Hash do arquivo bruto — auxilia rastreabilidade/idempotência."""
    h = hashlib.sha256()
    h.update(caminho.read_bytes())
    return h.hexdigest()


def ingerir(fonte: FonteBruta) -> pd.DataFrame:
    """Materializa UMA fonte bruta em data/raw/ e devolve o DataFrame bruto.

    Não transforma o conteúdo — apenas obtém, valida o boundary e lê.
    """
    destino = RAW_DIR / f"{fonte.nome}.{fonte.formato}"

    if fonte.url:
        _baixar(fonte.url, destino)
    elif fonte.caminho_local is not None:
        # Fonte local: copia para data/raw/ para manter o insumo versionável.
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(Path(fonte.caminho_local).read_bytes())
    else:
        raise ValueError(
            f"Fonte {fonte.nome!r} sem `url` nem `caminho_local`: nada a ingerir."
        )

    df = _ler_bruto(destino, fonte.formato)

    # Boundary validation: a fonte trouxe alguma coisa?
    if df.empty:
        raise ValueError(f"Fonte bruta {fonte.nome!r} veio vazia ({destino}).")

    # TODO: validar colunas mínimas ESPERADAS da fonte (fail fast). Ex.:
    # esperadas = {"municipio", "ano", "produto", "valor"}
    # faltando = esperadas - set(df.columns)
    # if faltando:
    #     raise ValueError(f"Colunas ausentes na fonte {fonte.nome!r}: {faltando}")

    print(
        f"[ingest] {fonte.nome}: {len(df)} linhas, {len(df.columns)} colunas "
        f"-> {destino}  (sha256={_sha256(destino)[:12]}…)  fonte={fonte.fonte!r}"
    )
    return df


def main() -> dict[str, pd.DataFrame]:
    """Ingere todas as FONTES e devolve um mapa {nome: DataFrame bruto}.

    `model.py` consome este mapa (ou relê os arquivos de data/raw/).
    """
    if not FONTES:
        raise SystemExit(
            "Nenhuma fonte declarada em FONTES. "
            "Edite pipeline/ingest.py e descreva a(s) fonte(s) bruta(s) do painel."
        )
    return {f.nome: ingerir(f) for f in FONTES}


if __name__ == "__main__":
    main()
