import os
import random
import time
from typing import Optional

import requests
from selectolax.lexbor import LexborHTMLParser

from ..utils.card import CardPrice, id_from_info
from ..utils.logger import setup_logger
from .fetch import get_response

logger = setup_logger("Yuyu-tei scraper", "logs/yuyutei_scraper.log")


class YuyuteiScraper:
    def __init__(self, kizu: str = ""):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": os.getenv("USER_AGENT"),
            "Cookie": os.getenv("YUYUTEI_COOKIE").replace("\n", "").strip(),
            "Accept-Language": "ja-JP,ja;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Referer": "https://yuyu-tei.jp/top/ygo"
        })

        self.kizu = kizu
        self.yuyutei_endpoint = f"https://yuyu-tei.jp/sell/ygo/s/search?search_word=&{kizu}"

    def scrape(self) -> list[CardPrice]:
        card_prices = []
        page = 2
        while True:
            response = get_response(self.session.get, self.yuyutei_endpoint)
            if not response:
                break

            self.session.headers.update({"Referer": self.yuyutei_endpoint})
            self.yuyutei_endpoint = self.yuyutei_endpoint + f"&page={page}"

            parser = LexborHTMLParser(response.text)
            items = parser.css("div.py-4.cards-list")
            if not items:
                break

            for item in items:
                rarity = self.parse_rarity(item)
                cards = item.css("div.card-product")
                for card in cards:
                    card_price = self.parse_card_price(card, rarity)
                    if card_price:
                        card_prices.append(card_price)
            """
            As Yuyutei prohibits information scraping on their website,
            I make an effort to limit the number of requests
            to one every 20 to 25 seconds.
            """
            time.sleep(random.randint(20, 25))
            logger.info(
                f"Yuyutei {'kizu' if self.kizu else ''} - Completed scraping page number: {page - 1}")
            page += 1

        return card_prices

    def parse_card_price(self, card, rarity: str) -> Optional[CardPrice]:
        try:
            name = card.css_first("h4.text-primary.fw-bold").text()
            price = int(card.css_first("strong[class^='d-block text-end']")
                        .text().split(" ")[0]
                        .replace(",", "")
                        )
            set_number = card.css_first("span.d-block.border.border-dark.p-1.w-100.text-center.my-2")
            set_number = "Undefined" if not set_number or set_number.text() == "-" else set_number.text()

            condition = "Scratch" if self.kizu else "Good"
            status = "Sold Out" if "sold-out" in card.attributes["class"] else "For Sale"
            id = id_from_info((set_number + rarity + condition + name).replace(" ", ""))
            return CardPrice(
                id=id,
                price=price,
                name=name,
                set_number=set_number,
                rarity=rarity,
                condition=condition,
                status=status,
                last_modified=int(time.time())
            )

        except AttributeError as e:
            logger.warning(f"Attribute Error: {e}")

        return None

    def parse_rarity(self, item) -> str:
        try:
            return item.css_first("span.py-2.d-inline-block.px-2.me-2.text-white.fw-bold").text()
        except AttributeError as e:
            logger.warning(f"Attribute Error: {e}")

        return ""
