#!/usr/bin/env python3
"""
ETL de extrato padronizado — VBP Paraná (eixo desempenho-economico).

Fonte primária (dados REAIS): repositório do painel avnergomes/vbp-parana,
arquivo processado dashboard/public/data/detailed.json (chave "mapData": VBP
agregado por municipio x ano, todos os produtos somados). Valores em R$
correntes; produção convertida para toneladas e área em hectares conforme o
pipeline preprocess_data.py do painel.

A chave geográfica canônica do Observatório (regional_idr = codigo creg_idr 01-23)
é anexada via JOIN por cod_ibge com o de-para canônico
assets/data/geo/municipios_ref_idr.csv (NUNCA por nome de município).

Gera:
  - vbp.csv / vbp.json        -> extrato COMPLETO padronizado (todos os anos)
  - vbp.sample.csv/.json      -> amostra fiel (anos âncora min/max, 399 mun.)

Uso: python _build_extract.py
"""
import csv
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEPARA = os.path.join(REPO_ROOT, "assets", "data", "geo", "municipios_ref_idr.csv")
SRC_URL = ("https://raw.githubusercontent.com/avnergomes/vbp-parana/"
           "main/dashboard/public/data/detailed.json")

COLS = ["cod_ibge", "municipio", "regional_idr", "reg_idr_nome",
        "meso_idr", "ano", "vbp_reais", "producao_ton", "area_ha"]


def load_depara(path):
    depara = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cod = row["cod_ibge"].strip().zfill(7)
            depara[cod] = {
                "creg_idr": row["creg_idr"].strip(),
                "reg_idr": row["reg_idr"].strip(),
                "meso_idr": row["meso_idr"].strip(),
            }
    if len(depara) != 399:
        print(f"AVISO: de-para com {len(depara)} municípios (esperado 399).",
              file=sys.stderr)
    return depara


def fetch_mapdata(url):
    print(f"Baixando fonte real: {url}", file=sys.stderr)
    with urllib.request.urlopen(url) as r:
        data = json.load(r)
    return data["mapData"]


def build_rows(mapdata, depara):
    rows = []
    unmatched = set()
    for rec in mapdata:
        cod = str(rec["c"]).zfill(7)
        dp = depara.get(cod)
        if dp is None:
            unmatched.add(cod)
            creg, regnome, meso = "", rec.get("r", ""), ""
        else:
            creg, regnome, meso = dp["creg_idr"], dp["reg_idr"], dp["meso_idr"]
        rows.append({
            "cod_ibge": cod,
            "municipio": rec.get("m", ""),
            "regional_idr": creg,
            "reg_idr_nome": regnome,
            "meso_idr": meso,
            "ano": rec["a"],
            "vbp_reais": rec["v"],
            "producao_ton": rec["p"],
            "area_ha": rec["ar"],
        })
    rows.sort(key=lambda x: (x["ano"], x["cod_ibge"]))
    if unmatched:
        print(f"AVISO: {len(unmatched)} cod_ibge sem match no de-para: "
              f"{sorted(unmatched)[:10]}", file=sys.stderr)
    return rows


def write_csv(path, data):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(data)


def write_json(path, data, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def main():
    depara = load_depara(DEPARA)
    mapdata = fetch_mapdata(SRC_URL)
    rows = build_rows(mapdata, depara)

    anos = sorted({r["ano"] for r in rows})
    ano_min, ano_max = anos[0], anos[-1]
    sample = [r for r in rows if r["ano"] in (ano_min, ano_max)]
    sample.sort(key=lambda x: (x["ano"], x["cod_ibge"]))

    write_csv(os.path.join(HERE, "vbp.csv"), rows)
    write_json(os.path.join(HERE, "vbp.json"), rows)
    write_csv(os.path.join(HERE, "vbp.sample.csv"), sample)
    write_json(os.path.join(HERE, "vbp.sample.json"), sample, indent=0)

    print(f"OK: {len(rows)} linhas totais (anos {ano_min}-{ano_max}); "
          f"amostra {len(sample)} linhas "
          f"({len({r['cod_ibge'] for r in sample})} municípios).",
          file=sys.stderr)


if __name__ == "__main__":
    main()
