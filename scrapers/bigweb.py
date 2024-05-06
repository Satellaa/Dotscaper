import json
import os
import random
import time
from typing import Optional

import requests

from utils.card import CardPrice
from utils.logger import setup_logger
from utils.string_manip import half_to_full

from .fetch import get_response

logger = setup_logger("Bigweb scraper", "logs/bigweb_scraper.log")


class BigwebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.getenv("USER_AGENT"),
            "Cookie": os.getenv("BIGWEB_API_COOKIE").replace("\n", "").strip(),
            # pylint: disable=line-too-long
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9.image/avif,jimage/webpimage/apng*/*;q=0.8,application/signed exchange:v-b3;q-0.7",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        })

        self.rarity_alias = self.load_rarity_alias()

    def scrape(self, page: int = 1) -> list[CardPrice]:
        card_prices = []
        while True:
            url = f"https://api.bigweb.co.jp/products?game_id=9&page={page}"
            response = get_response(self.session.get, url)
            if not response:
                break

            data = response.json()
            raw_cards = data["items"]
            if len(raw_cards) == 0:
                break

            for raw_card in raw_cards:
                card_price = self.parse_card_price(raw_card)
                if card_price:
                    card_prices.append(card_price)

            if page >= int(data["pagenate"]["pageCount"]):
                break

            time.sleep(random.randint(5, 6))
            logger.info(f"Bigweb - Completed scraping page number: {page}")
            page += 1

        return card_prices

    def parse_card_price(self, raw_card_price: dict) -> Optional[CardPrice]:
        """
        use try-except instead of dict's get method because any "raw_card_price" missing the
        necessary fields is invalid, for example a product that is not a card.
        """
        try:
            id = raw_card_price["id"]
            price = int(raw_card_price["price"])
            name = half_to_full(raw_card_price["name"])
            set_number = raw_card_price["fname"].upper().strip()
            rarity = self.parse_rarity(raw_card_price["rarity"])
            status = "Sold Out" if raw_card_price["is_sold_out"] else "For Sale"
            condition = "Scratch" if raw_card_price["condition"]["slip"] == "特価[傷含む]" else "Good"
            comment = raw_card_price["comment"]

            return CardPrice(
                id=id,
                price=price,
                name=name,
                set_number=set_number,
                rarity=rarity,
                condition=condition,
                status=status,
                last_modified=int(time.time()),
                comment=comment
            )

        except Exception as e:
            logger.warning(e)
            return None

    def parse_rarity(self, rarity: Optional[dict]) -> str:
        if not rarity:
            return ""

        rarity = rarity["slip"].strip()
        if rarity in self.rarity_alias:
            return self.rarity_alias[rarity]

        return rarity

    def load_rarity_alias(self) -> dict:
        with open("./alias/rarity.json", "r", encoding="utf-8") as f:
            return json.load(f)
