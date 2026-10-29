import sys

import pandas as pd

inventario_path, spiders_path = sys.argv[1], sys.argv[2]
inv = pd.read_csv(inventario_path, dtype={"codigo_ibge": str}, parse_dates=["data"])
spiders = pd.read_csv(
    spiders_path, dtype={"codigo_ibge": str}, parse_dates=["start_date"]
)

# Spider vigente na data do arquivo: maior start_date <= data
inv = inv.sort_values("data")
spiders = spiders.sort_values("start_date")
df = pd.merge_asof(
    inv,
    spiders,
    left_on="data",
    right_on="start_date",
    by="codigo_ibge",
    direction="backward",
)
sem_match = df["spider"].isna()
if sem_match.any():
    # fallback: território com spider, mas arquivo anterior ao start_date
    fb = inv[sem_match.values].merge(
        spiders.drop_duplicates("codigo_ibge"), on="codigo_ibge", how="left"
    )
    df.loc[sem_match, ["spider", "spider_base", "zyte"]] = fb[
        ["spider", "spider_base", "zyte"]
    ].values
df["spider_base"] = df["spider_base"].fillna("sem spider atual")
df["ano"] = df["data"].dt.year
df["ext_s3"] = df["s3_key"].str.extract(r"(\.[a-z0-9]+)$")[0].fillna("(sem extensão)")
df.to_csv(sys.argv[3], index=False)

print(
    "arquivos:",
    len(df),
    "| municípios:",
    df.codigo_ibge.nunique(),
    "| spiders:",
    df.spider.nunique(),
)
print("\n== extensão no S3 (arquivo é HTML de fato) ==")
print(df.ext_s3.value_counts().to_string())
print("\n== por spider base ==")
g = (
    df.groupby("spider_base")
    .agg(
        arquivos=("gazette_id", "size"),
        municipios=("codigo_ibge", "nunique"),
        de=("data", "min"),
        ate=("data", "max"),
    )
    .sort_values("arquivos", ascending=False)
)
g["pct"] = (100 * g.arquivos / len(df)).round(1)
print(g.to_string())
print("\n== por ano ==")
print(df.groupby("ano").size().to_string())
corte = pd.Timestamp("2026-06-19")  # últimos 3 meses antes do job (2026-09-19)
print("\n== recorrência: municípios com arquivo HTML nos últimos 3 meses ==")
rec = (
    df[df.data >= corte]
    .groupby(["spider_base"])
    .agg(municipios=("codigo_ibge", "nunique"), arquivos=("gazette_id", "size"))
)
print(rec.sort_values("arquivos", ascending=False).to_string())
print("\n== fora do bloco ADiarios: por spider ==")
fora = df[df.spider_base != "BaseAdiariosV1Spider"]
print(len(fora), "arquivos")
s = (
    fora.groupby(["uf", "municipio", "spider", "spider_base"])
    .agg(arquivos=("gazette_id", "size"), de=("data", "min"), ate=("data", "max"))
    .sort_values("arquivos", ascending=False)
)
print(s.to_string())
