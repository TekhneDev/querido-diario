"""Resume o inventário enriquecido por conteúdo salvo e gera o gráfico."""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

enriquecido, conteudo, grafico = sys.argv[1], sys.argv[2], sys.argv[3]
df = pd.read_csv(enriquecido, parse_dates=["data"])
cont = pd.read_csv(conteudo)
df = df.merge(cont, on="spider", how="left")
df.loc[
    df.spider_base == "BaseAdiariosV1Spider", "conteudo_salvo"
] = "Desafio Cloudflare Turnstile"
df["conteudo_salvo"] = df["conteudo_salvo"].fillna("Não amostrado (spider removido)")

resumo = (
    df.groupby("conteudo_salvo")
    .agg(arquivos=("gazette_id", "size"), municipios=("codigo_ibge", "nunique"))
    .sort_values("arquivos", ascending=False)
)
resumo["pct"] = (100 * resumo.arquivos / len(df)).round(1)
print(resumo.to_markdown())

df["grupo"] = df.spider_base.where(
    df.spider_base == "BaseAdiariosV1Spider", "Demais spiders"
)
df["grupo"] = df["grupo"].replace({"BaseAdiariosV1Spider": "ADiarios v1 (Cloudflare)"})
por_ano = df.groupby([df.data.dt.year, "grupo"]).size().unstack(fill_value=0)
por_ano = por_ano.reindex(
    range(por_ano.index.min(), por_ano.index.max() + 1), fill_value=0
)

fig, ax = plt.subplots(figsize=(10, 4.5))
por_ano.plot(kind="bar", stacked=True, ax=ax, color=["#d1495b", "#00798c"], width=0.8)
ax.set_title("Arquivos HTML salvos no lugar do diário, por ano da edição (#1483)")
ax.set_xlabel("Ano da edição")
ax.set_ylabel("Arquivos")
ax.set_yscale("symlog", linthresh=10)
ax.legend(title=None, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
labels = [
    str(y) if (y % 2 == 0 or y == por_ano.index.max()) else "" for y in por_ano.index
]
ax.set_xticklabels(labels, rotation=0)
fig.tight_layout()
fig.savefig(grafico, dpi=150)
