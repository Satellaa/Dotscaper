from typing import Optional

from pymongo import UpdateOne
from pymongo.collection import Collection

from ..utils.card import Card, CardPrice
from ..utils.logger import setup_logger
from ..utils.query import create_name_filter

logger = setup_logger("card price updater", "logs/card_price_updater.log")


class CardPriceUpdater:
    def __init__(self, coll: Collection[Card], market: str, check_safe: bool = False):
        self.coll = coll
        self.market = market
        self.operations = []

        self.all_cards = list(coll.find())

        self.card_language = "en" if self.market == "tcg_corner" else "ja"
        self.set_locale = "ae" if self.market == "tcg_corner" else "ja"

        self.check_safe = check_safe
        if check_safe:
            # "Token Thanksgiving", "Token Feastevil", "Token Sundae", "Oh Tokenbaum!"
            self.token_in_name_list = [6364, 5733, 9348, 10467]
            self.token_prefix_list = ["JPT", "JPS"]
            self.unsafe_prefix_list = ["-EN", "JPP", "-AE"]
            self.unsafe_comment_list = ["-EN", "-AE"]

    def execute(self):
        if self.operations:
            self.coll.bulk_write(self.operations, ordered=False)
        else:
            logger.debug("There are no operations to complete.")

    def add(self, card_prices: Optional[list[CardPrice]]):
        if not card_prices:
            return

        for card_price in card_prices:
            try:
                if (operation := self.create_update_operation(card_price)):
                    self.operations.append(operation)
            except KeyError as e:
                logger.warning(
                    f"card price: {card_price} ---- does not have a key name: {e}")

    def create_update_operation(
            self, card_price: CardPrice) -> Optional[UpdateOne]:
        card = self.find_card(card_price)
        if not card:
            return None

        document_id = card["_id"]
        path = f"card_prices.{self.market}"
        existing_price = next(
            (cp for cp in card["card_prices"][self.market] if cp["id"] == card_price["id"]), None)
        card_price.pop("comment", None)
        card_price.pop("name", None)
        update = None

        if existing_price:
            filter = {"_id": document_id, f"{path}.id": card_price["id"]}

            if card_price["price"] and card_price["price"] != existing_price["price"]:
                update = {"$set": {f"{path}.$": card_price}}
            elif card_price["status"] != existing_price["status"]:
                update = {
                    "$set": {
                        f"{path}.$.status": card_price["status"],
                        f"{path}.$.last_modified": card_price["last_modified"],
                    }
                }
        elif card_price["price"]:
            filter = {"_id": document_id}
            update = {"$addToSet": {path: card_price}}

        if update:
            return UpdateOne(filter, update)

        return None

    def find_card(self, card_price: CardPrice) -> Optional[Card]:
        name_pipeline = [create_name_filter(
            f"{self.card_language}", card_price["name"])]

        if (card := self.find_card_with_set_number(card_price["set_number"])):
            return card
        if (card := next(self.coll.aggregate(name_pipeline), None)):
            if self.check_safe:
                return self.to_safe(card_price, card)
            return card

        return None

    """
	Honestly, I can't think of a way to do the same thing as
	this function but with a MongoDB query
	"""

    def find_card_with_set_number(self, set_number: str) -> Optional[Card]:
        return next(
            (card for card in self.all_cards for set in card["sets"][self.set_locale] if set["set_number"] in set_number), None)

    def to_safe(self, card_price: CardPrice, card: Card) -> Optional[Card]:
        if self.is_token(card_price, card):
            card = self.coll.find_one({"konami_id": 0})
        elif self.is_unsafe(card_price):
            return None

        if card["name"]["ja"] != card_price["name"] and card["konami_id"] != 0:
            logger.debug(
                f"id {
                    card['_id']}: {
                    card_price['name']} != {
                    card['name']['ja']}")

        return card

    def is_token(self, card_price: CardPrice, card: Card) -> bool:
        return ("トークン" in card_price["name"] and
                not card["konami_id"] in self.token_in_name_list or
                self.is_in(card_price["set_number"], self.token_prefix_list))

    def is_unsafe(self, card_price: CardPrice) -> bool:
        return (self.is_in(card_price["set_number"], self.unsafe_prefix_list) or
                self.market == "bigweb" and (self.is_in(card_price["comment"], self.unsafe_comment_list) or
                not card_price["comment"]) or
                card_price["rarity"] == "-")

    def is_in(self, string: str, arr: list) -> bool:
        return any(e in string for e in arr)
