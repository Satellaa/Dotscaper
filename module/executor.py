from pymongo.collection import Collection
from pymongo.mongo_client import MongoClient
from trio import open_nursery
from trio.to_thread import run_sync

from .scrapers.bigweb import BigwebScraper
from .scrapers.tcg_corner import TCGCornerScraper
from .scrapers.yaml_yugi import YAMLYugiScraper
from .scrapers.yugipedia import YugipediaScraper
from .scrapers.yuyutei import YuyuteiScraper
from .updaters.card import CardUpdater
from .updaters.card_price import CardPriceUpdater
from .utils.card import Card


class Executor:
    def __init__(self, uri: str, db: str, coll: str):
        self.client = MongoClient(uri)
        self.db = self.client[db]
        self.coll: Collection[Card] = self.db[coll]

        self.info_scrapers = {
            "YAML Yugi": YAMLYugiScraper(),
            "Yugipedia": YugipediaScraper(),
        }

        self.prices_scrapers = {
            "Bigweb": [BigwebScraper()],
            "Yuyutei": [YuyuteiScraper(), YuyuteiScraper("kizu=1")],
            "TCG Corner": [TCGCornerScraper()]
        }

        self.updaters = {
            "Card info": CardUpdater(self.coll),
            "TCG Corner": CardPriceUpdater(self.coll, "tcg_corner"),
            "Bigweb": CardPriceUpdater(self.coll, "bigweb", True),
            "Yuyutei": CardPriceUpdater(self.coll, "yuyutei", True)
        }

    def update_cards(self, source):
        cards: list[Card] = []
        if source == "YAML Yugi":
            cards += self.info_scrapers[source].scrape()
        elif source == "Yugipedia":
            cards += self.info_scrapers[source].scrape_all()
        elif source == "All":
            cards += self.info_scrapers["YAML Yugi"].scrape()
            cards += self.info_scrapers["Yugipedia"].scrape_all()

        self.updaters["Card info"].add(cards)
        self.updaters["Card info"].execute()

    async def update_prices(self, markets):
        async with open_nursery() as nursery:
            for market in markets:
                if market in self.prices_scrapers and market in self.updaters:
                    for scraper in self.prices_scrapers[market]:
                        nursery.start_soon(
                            run_sync,
                            self.task,
                            scraper,
                            self.updaters[market]
                        )

    def task(self, scraper, updater):
        prices = scraper.scrape()
        updater.add(prices)
        updater.execute()
