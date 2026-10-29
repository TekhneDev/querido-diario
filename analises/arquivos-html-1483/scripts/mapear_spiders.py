"""Gera o mapa território IBGE -> spider -> spider base a partir do código."""
import csv
import sys

from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader

from gazette import settings

loader = SpiderLoader.from_settings(
    Settings({"SPIDER_MODULES": settings.SPIDER_MODULES})
)
writer = csv.writer(sys.stdout)
writer.writerow(["codigo_ibge", "spider", "spider_base", "start_date", "zyte"])
for name in sorted(loader.list()):
    cls = loader.load(name)
    bases = [
        c.__name__
        for c in cls.__mro__[1:]
        if c.__module__.startswith("gazette.spiders.base.")
    ]
    base = bases[0] if bases else "individual"
    writer.writerow(
        [
            getattr(cls, "TERRITORY_ID", ""),
            name,
            base,
            getattr(cls, "start_date", ""),
            getattr(cls, "zyte_smartproxy_enabled", False),
        ]
    )
