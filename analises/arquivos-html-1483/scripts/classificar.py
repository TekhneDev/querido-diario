import csv
import re
import sys
from pathlib import Path

from scrapy.http import Response

from gazette.utils.blocking import is_cloudflare_challenge
from gazette.utils.files import detect_file_type

amostra_csv, pasta, saida = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
out = []
for row in csv.DictReader(open(amostra_csv)):
    body = (pasta / row["gazette_id"]).read_bytes()
    resp = Response(row["url_publica"], body=body)
    title = re.search(rb"<title[^>]*>(.*?)</title>", body[:20000], re.I | re.S)
    title = title.group(1).decode("utf-8", "replace").strip()[:70] if title else ""
    out.append(
        {
            **row,
            "tipo_detectado": detect_file_type(resp),
            "cloudflare": is_cloudflare_challenge(resp),
            "bytes": len(body),
            "titulo": " ".join(title.split()),
        }
    )
w = csv.DictWriter(open(saida, "w"), fieldnames=out[0].keys())
w.writeheader()
w.writerows(out)
from collections import Counter

print("tipo detectado:", Counter(r["tipo_detectado"] for r in out))
print(
    "cloudflare:",
    Counter((r["spider_base"] == "BaseAdiariosV1Spider", r["cloudflare"]) for r in out),
)
for r in out:
    if r["spider_base"] != "BaseAdiariosV1Spider" or r["tipo_detectado"] != "html":
        print(
            f'{r["spider"]:28} {r["data"][:10]} {r["tipo_detectado"]:5} {r["bytes"]:>8} cf={r["cloudflare"]!s:5} {r["titulo"]}'
        )
