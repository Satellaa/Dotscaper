import os
import random
import time
from typing import Optional

import requests
from selectolax.lexbor import LexborHTMLParser

from ..utils.card import CardPrice
from ..utils.logger import setup_logger
from .fetch import get_response

logger = setup_logger("TCG Corner scraper", "logs/tcg_corner_scraper.log")


class TCGCornerScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.getenv("USER_AGENT"),
            "Cookie": os.getenv("TCG_CORNER_COOKIE").replace("\n", "").strip(),
            "Accept-Language": "ja-JP,ja;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Referer": "https://tcg-corner.com"
        })

        self.tcg_corner_endpoint = "https://tcg-corner.com/collections/yu-gi-oh-single-card-asia-english"

    def scrape(self) -> list[CardPrice]:
        card_prices = []
        page = 2
        while True:
            response = get_response(self.session.get, self.tcg_corner_endpoint)
            if not response:
                break

            self.session.headers.update({"Referer": self.tcg_corner_endpoint})
            self.tcg_corner_endpoint = f"https://tcg-corner.com/collections/yu-gi-oh-single-card-asia-english?&page={
                page}"

            parser = LexborHTMLParser(response.text)
            collection_items = parser.css('div.collection__item')

            if len(collection_items) <= 0:
                break

            for item in collection_items:
                card_price = self.parse_card_price(item)
                if card_price:
                    card_prices.append(card_price)
            """
			As TCG Corner prohibits information scraping on their website,
			I make an effort to limit the number of requests
			to one every 20 to 25 seconds.
			"""
            time.sleep(random.randint(20, 25))
            logger.info(
                f"TCG Corner - Completed scraping page number: {page - 1}")
            page += 1

        return card_prices

    def parse_card_price(self, item) -> Optional[CardPrice]:
        try:
            a_tag = item.css_first("div.product-card__meta-info a")
            raw_price = item.css_first(
                "span.price-item--regular[data-product-price]").text()

            name = a_tag.text().strip()
            info = name.split(" ")

            set_number = info[0]
            rarity = info[-1]
            price = int(
                raw_price.split(" ")[0].replace(
                    "¥", "").replace(
                    ",", ""))
            status = "Sold Out" if item.css_first("li.product-card__label product-card__label--sold-out") else "For Sale"

            if rarity.startswith("("):
                rarity = rarity.strip("()")
            else:  # case where there is no "(rarity)" in it
                rarity = self.parse_rarity(a_tag)

            card_price = CardPrice(
                id=self.id_from_info(set_number + rarity),
                price=price,
                name=name,
                set_number=set_number,
                rarity=rarity,
                condition="Good",
                status=status,
                last_modified=int(time.time())
            )
            return card_price

        except AttributeError as e:
            logger.warning(f"Attribute Error: {e}")

        return None

    def parse_rarity(self, a_tag) -> str:
        time.sleep(random.randint(10, 15))

        url = f"https://tcg-corner.com{a_tag.attrs['href']}"
        response = get_response(self.session.get, url)

        if response:
            parser = LexborHTMLParser(response.text)
            for br in parser.tags('br'):
                next_s = br.next
                if next_s and "Rarity" in next_s.text():
                    return next_s.text().split(":")[1].strip()

        return "Undefined"

    def id_from_info(self, info: str) -> int:
        return int(
            str(int.from_bytes(info.upper().strip().encode(), byteorder='big'))[0:6])
