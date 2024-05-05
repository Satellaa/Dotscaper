from utils.card import Card, CardPrice
from utils.filter import Filter
from utils.string_manip import half_to_full
from utils.logger import setup_logger
from pymongo import UpdateOne
from pymongo.collection import Collection
from typing import Optional

logger = setup_logger("card info updater", "card_info_updater.log")

class CardUpdater:
	def __init__(self, coll: Collection[Card]):
		self.coll = coll
		self.operations = []
	
	def execute(self):
		if self.operations:
			self.coll.bulk_write(self.operations, ordered=False)
			self.set_card_prices_field()
		else:
			logger.debug("There are no operations to complete.")
	
	def set_card_prices_field(self):
		filter = {"card_prices": {"$exists": False}}
		card_prices = {"card_prices": {"bigweb": [], "yuyutei": [], "tcg_corner": []}}
		
		self.coll.update_many(filter, {"$set": card_prices})
	
	def add(self, cards: Optional[list[Card]]):
		if not cards:
			return
		
		for card in cards:
			try:
				operation = self.create_update_operation(card)
				self.operations.append(operation)
			except KeyError as e:
				logger.warning(f"card: {card} ---- {e}")
	
	def create_update_operation(self, card: Card) -> UpdateOne:
		filter = {"konami_id": card["konami_id"]} if card["konami_id"] > 0 else {"name.en": card["name"]["en"]}
		
		sets = card.pop("sets")
		ja_sets = {"$each": sets.get("ja", [])}
		ae_sets = {"$each": sets.get("ae", [])}
		
		card["name"]["ja"] = half_to_full(card["name"]["ja"])
		
		set_or_set_on_insert = "$set" if card["konami_id"] > 0 else "$setOnInsert"
		update = {
			f"{set_or_set_on_insert}": card,
			"$addToSet": {"sets.ja": ja_sets, "sets.ae": ae_sets}
		}
		
		return UpdateOne(filter, update, upsert=True)