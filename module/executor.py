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
        self.client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")

        self.db = self.client[db]
        self.coll: Collection[Card] = self.db[coll]

        self.yaml_scraper = YAMLYugiScraper()
        self.yugipedia_scraper = YugipediaScraper()
        self.bigweb_scraper = BigwebScraper()
        self.yuyutei_scraper = YuyuteiScraper()
        self.yuyutei_kizu_scraper = YuyuteiScraper("kizu=1")
        self.tcg_corner_scraper = TCGCornerScraper()

        self.card_info_updater = CardUpdater(self.coll)
        self.tcg_corner_updater = CardPriceUpdater(self.coll, "tcg_corner")
        self.bigweb_updater = CardPriceUpdater(self.coll, "bigweb", True)
        self.yuyutei_updater = CardPriceUpdater(self.coll, "yuyutei", True)

    """
	You need to have card information from YAMIYugi first before you can
	update/insert information from Yugipedia properly.
	"""

    def update_cards(self, update_yaml_yugi=True, update_yugipedia=False):
        cards: list[Card] = []
        if update_yaml_yugi and (yaml_cards := self.yaml_scraper.scrape()):
            cards += yaml_cards
        if update_yugipedia and (
                yugipedia_cards := self.yugipedia_scraper.scrape_all()):
            cards += yugipedia_cards

        self.card_info_updater.add(cards)
        self.card_info_updater.execute()

    async def update_prices(
            self,
            update_bigweb: bool = False,
            update_yuyutei: bool = False,
            update_tcg_corner: bool = False):
        async with open_nursery() as nursery:
            if update_bigweb:
                nursery.start_soon(
                    run_sync,
                    self.task,
                    self.bigweb_scraper,
                    self.bigweb_updater)

            if update_yuyutei:
                nursery.start_soon(
                    run_sync,
                    self.task,
                    self.yuyutei_scraper,
                    self.yuyutei_updater)

                nursery.start_soon(
                    run_sync,
                    self.task,
                    self.yuyutei_kizu_scraper,
                    self.yuyutei_updater)

            if update_tcg_corner:
                nursery.start_soon(
                    run_sync,
                    self.task,
                    self.tcg_corner_scraper,
                    self.tcg_corner_updater)

    def task(self, scraper, updater):
        prices = scraper.scrape()
        updater.add(prices)
        updater.execute()
