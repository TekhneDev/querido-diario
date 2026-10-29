import sys

import pandas as pd

df = pd.read_csv(sys.argv[1], parse_dates=["data"])
rows = []
for spider, g in df.sort_values("data").groupby("spider"):
    idx = sorted({0, len(g) // 2, len(g) - 1})
    if g.spider_base.iloc[0] == "BaseAdiariosV1Spider":
        idx = [len(g) - 1]
    rows.append(g.iloc[idx])
pd.concat(rows)[["gazette_id", "spider", "spider_base", "data", "url_publica"]].to_csv(
    sys.argv[2], index=False
)
