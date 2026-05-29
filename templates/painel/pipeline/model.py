"""model.py — Etapa 2 do pipeline de um painel temático.

Observatório Rural Paranaense — cookiecutter de painel.
Ordem do pipeline:  ingest  ->  model  ->  export_open_data  ->  (report)

RESPONSABILIDADE DESTA ETAPA
----------------------------
Aqui mora a REGRA DE NEGÓCIO do painel:
  - limpar e tipar as colunas brutas (renomear para o esquema publicado);
  - juntar/combinar fontes (joins);
  - AGREGAR ao nível de publicação (estado / mesorregião / regional / município);
  - NORMALIZAR a chave geográfica `regional_idr` usando o DE-PARA CANÔNICO
    `assets/data/geo/municipios_ref_idr.csv` (junção por chave, NUNCA por nome);
  - garantir a regra LGPD: o resultado contém SÓ AGREGADOS, sem CPF/CNPJ
    (a anonimização/agregação acontece aqui, antes de qualquer arquivo público).

A saída desta etapa é um DataFrame "tidy" (uma observação por linha) pronto para
ser publicado por `export_open_data.py`.

Convenções (ver docs/DADOS-ABERTOS.md §4 e docs/GEO.md §2):
  - Chave canônica: `regional_idr` == `creg_idr` (código do núcleo, STRING com
    zero à esquerda: "01".."23", SEM "08"). `reg_idr` é só rótulo humano.
  - Datasets municipais carregam `cod_ibge` (7 dígitos, string) e DEVEM derivar
    `regional_idr` via de-para. Datasets já regionais usam `regional_idr` direto.
  - Não duplicar o de-para dentro do dataset de domínio: derivar e descartar
    o excesso (manter só as colunas geográficas necessárias).
  - Imutabilidade: NÃO mutar DataFrames in-place; sempre devolver cópias novas.

Uso:
    python -m pipeline.model
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import ingest

# ---------------------------------------------------------------------------
# Caminhos canônicos. O de-para geográfico vive SÓ no hub (fonte única).
# Quando o painel é um repo separado, aponte DEPARA_CSV para a cópia do hub
# (URL estável) ou para um submódulo/cópia versionada — NUNCA recriar o mapa.
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

# TODO: ajustar para o caminho real do de-para no contexto do painel.
DEPARA_CSV = REPO_ROOT / "assets" / "data" / "geo" / "municipios_ref_idr.csv"

# Colunas REAIS do de-para canônico (confirmadas em assets/data/geo/
# municipios_ref_idr.csv): cod_ibge, municipio, creg_idr, reg_idr, meso_idr.
DEPARA_COLS = ("cod_ibge", "municipio", "creg_idr", "reg_idr", "meso_idr")


def carregar_depara() -> pd.DataFrame:
    """Carrega o de-para canônico município -> regional -> mesorregião.

    Lê tudo como STRING para preservar zeros à esquerda de `creg_idr`/`cod_ibge`.
    Falha rápido se o arquivo ou as colunas esperadas não existirem (boundary).
    """
    if not DEPARA_CSV.exists():
        raise FileNotFoundError(
            f"De-para geográfico não encontrado: {DEPARA_CSV}. "
            "Ver docs/GEO.md — a chave canônica é regional_idr."
        )

    depara = pd.read_csv(DEPARA_CSV, dtype=str, keep_default_na=False)

    faltando = set(DEPARA_COLS) - set(depara.columns)
    if faltando:
        raise ValueError(f"De-para sem colunas esperadas: {sorted(faltando)}")

    # `creg_idr` é a materialização da chave canônica regional_idr.
    # Garante zero-pad de 2 dígitos para casar com o mapa SVG (cod numérico).
    out = depara.copy()
    out["cod_ibge"] = out["cod_ibge"].str.strip()
    out["creg_idr"] = out["creg_idr"].str.strip().str.zfill(2)
    out = out.rename(columns={"creg_idr": "regional_idr"})  # nome publicado
    return out[["cod_ibge", "municipio", "regional_idr", "reg_idr", "meso_idr"]]


def normalizar_regional_idr(
    df: pd.DataFrame,
    chave_municipal: str = "cod_ibge",
) -> pd.DataFrame:
    """Anexa `regional_idr` (e rótulos) a um DataFrame municipal via de-para.

    Junção SEMPRE por chave forte (`cod_ibge`), NUNCA por nome de município.
    Devolve uma cópia nova (imutabilidade); valida que não sobraram municípios
    sem correspondência (boundary), o que indicaria `cod_ibge` inválido.
    """
    if chave_municipal not in df.columns:
        raise ValueError(
            f"Coluna de junção {chave_municipal!r} ausente; sem ela não há como "
            "derivar regional_idr (ver docs/GEO.md §4)."
        )

    depara = carregar_depara()

    base = df.copy()
    base[chave_municipal] = base[chave_municipal].astype(str).str.strip()

    juntado = base.merge(
        depara,
        how="left",
        left_on=chave_municipal,
        right_on="cod_ibge",
        suffixes=("", "_geo"),
    )

    sem_regional = juntado["regional_idr"].isna().sum()
    if sem_regional:
        # Falha rápido: códigos IBGE fora do PR ou inválidos não devem passar.
        amostra = (
            juntado.loc[juntado["regional_idr"].isna(), chave_municipal]
            .drop_duplicates()
            .head(10)
            .tolist()
        )
        raise ValueError(
            f"{sem_regional} linha(s) sem regional_idr após o join. "
            f"Verifique cod_ibge (amostra sem match: {amostra})."
        )
    return juntado


def aplicar_supressao_lgpd(
    df: pd.DataFrame,
    coluna_contagem: str | None = None,
    n_minimo: int = 3,
) -> pd.DataFrame:
    """Garante a regra LGPD: só agregados; suprime células pequenas.

    O portal público expõe SOMENTE dados agregados (docs/DADOS-ABERTOS.md §6).
    - NUNCA deixe passar CPF/CNPJ/NIT/CAF individual, nome de produtor,
      coordenada de imóvel etc. — remova tais colunas no `transformar`.
    - Quando há contagem de unidades por célula, suprima as com n < n_minimo
      (risco de reidentificação) e registre a supressão em `notas` do dataset.

    Devolve uma cópia nova. Por padrão é no-op se `coluna_contagem` for None.
    """
    # TODO: garantir que NÃO existem colunas identificáveis no df antes de publicar.
    proibidas = {"cpf", "cnpj", "nit", "caf", "nome_produtor", "inscricao_estadual"}
    presentes = proibidas & {c.lower() for c in df.columns}
    if presentes:
        raise ValueError(
            f"Colunas identificáveis presentes (proibido publicar): {sorted(presentes)}. "
            "Agregue/remova em model.py antes de exportar (LGPD)."
        )

    if coluna_contagem is None:
        return df.copy()

    out = df.copy()
    pequenas = out[coluna_contagem].astype("Int64") < n_minimo
    # Mascarar o valor sensível das células pequenas (ex.: zerar/anular a métrica).
    # TODO: definir POLÍTICA de supressão do painel (anular métrica vs. agrupar).
    out.loc[pequenas, coluna_contagem] = pd.NA
    return out


def transformar(brutos: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """REGRA DE NEGÓCIO do painel: do bruto ao DataFrame publicável (tidy).

    `brutos` é o mapa {nome: DataFrame} devolvido por ingest.main().

    Etapas típicas (adapte ao painel):
      1) selecionar/renomear colunas para o ESQUEMA PUBLICADO (nomes do dicionário);
      2) tipar (datas ISO, decimais com ponto, códigos como string);
      3) juntar fontes;
      4) AGREGAR ao nível de publicação;
      5) derivar `regional_idr` via normalizar_regional_idr (se municipal);
      6) aplicar_supressao_lgpd;
      7) ordenar e devolver.
    """
    # TODO: substituir todo o corpo por baixo pela lógica real do painel.
    raise NotImplementedError(
        "Implemente a regra de negócio do painel em transformar(). "
        "Exemplo de fluxo abaixo (comentado)."
    )

    # ---- EXEMPLO ilustrativo (descomente e adapte) ------------------------
    # bruto = brutos["vbp-bruto"].copy()
    #
    # # 1) renomear para o esquema publicado (nomes do DICIONARIO)
    # df = bruto.rename(columns={
    #     "COD_MUN":  "cod_ibge",
    #     "ANO":      "ano",
    #     "PRODUTO":  "produto",
    #     "VALOR_RS": "vbp_reais",
    # })
    #
    # # 2) tipagem (decimal com ponto; código como string)
    # df["cod_ibge"]  = df["cod_ibge"].str.zfill(7)
    # df["ano"]       = df["ano"].astype("Int64")
    # df["vbp_reais"] = pd.to_numeric(df["vbp_reais"], errors="raise")
    #
    # # 4) agregar (só agregados!)
    # df = (df.groupby(["cod_ibge", "ano", "produto"], as_index=False)["vbp_reais"]
    #         .sum())
    #
    # # 5) derivar regional_idr via de-para (join por chave)
    # df = normalizar_regional_idr(df, chave_municipal="cod_ibge")
    #
    # # 6) checar/aplicar LGPD
    # df = aplicar_supressao_lgpd(df)
    #
    # # 7) ordenar e selecionar colunas finais do dataset publicado
    # cols = ["cod_ibge", "municipio", "regional_idr", "reg_idr", "meso_idr",
    #         "ano", "produto", "vbp_reais"]
    # return df[cols].sort_values(cols).reset_index(drop=True)


def main() -> pd.DataFrame:
    """Roda ingest -> transform e devolve o DataFrame publicável."""
    brutos = ingest.main()
    df = transformar(brutos)
    if df.empty:
        raise ValueError("model.transformar() devolveu DataFrame vazio.")
    print(f"[model] dataset publicável: {len(df)} linhas, colunas={list(df.columns)}")
    return df


if __name__ == "__main__":
    main()
