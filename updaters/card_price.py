from utils.card import Card, CardPrice
from utils.filter import Filter
from utils.logger import setup_logger
from pymongo import UpdateOne
from pymongo.collection import Collection
from typing import Optional

logger = setup_logger("card price updater", "card_price_updater.log")

class CardPriceUpdater:
	def __init__(self, coll: Collection[Card], market: str):
		self.coll = coll
		self.market = market
		self.operations = []
		
		self.all_cards = list(coll.find())
		
		self.card_language = "en" if self.market == "tcg_corner" else "ja"
		self.set_locale = "ae" if self.market == "tcg_corner" else "ja"
		
		# Bigweb only
		if market == "bigweb":
			# "Token Thanksgiving", "Token Feastevil", "Token Sundae", "Oh Tokenbaum!"
			self.token_in_name_list = [6364, 5733, 9348, 10467]
			self.token_prefix_list = ["JPT", "JPS"]
			self.unsafe_prefix_list = ["-EN", "JPP", "-AE"]
			self.unsafe_comment_list = ["-EN", "-AE"]
		# end
	
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
			except AttributeError as e:
				logger.warning(f"card price: {card} ---- {e}")
	
	def create_update_operation(self, card_price: CardPrice) -> Optional[UpdateOne]:
		card = self.find_card(card_price)
		if not card:
			return None
		
		konami_id = card["konami_id"]
		path = f"card_prices.{self.market}"
		existing_price = next((cp for cp in card["card_prices"][self.market] if cp["id"] == card_price["id"]), None)
		card_price.pop("comment", None)
		update = None
		if existing_price:
			
			filter = {"konami_id": konami_id, f"{path}.id": card_price["id"]}
			
			if card_price["price"] and card_price["price"] != existing_price["price"]:
				update =  {"$set": {f"{path}.$": card_price}}
			elif card_price["status"] != existing_price["status"]:
				update = {
					"$set": {
						f"{path}.$.status": card_price["status"],
						f"{path}.$.last_modified": card_price["last_modified"],
					}
				}
		elif card_price["price"]:
			filter = {"konami_id": konami_id}
			update = {"$push": {path: card_price}}
		
		if update:
			return UpdateOne(filter, update)
		
		return None
	
	def find_card(self, card_price: CardPrice) -> Optional[Card]:
		name_pipeline = [Filter.create_name_filter(f"{self.card_language}", card_price["name"])]
		
		if (card := self.find_card_with_set_number(card_price["set_number"])):
			return card
		elif (card := next(self.coll.aggregate(name_pipeline), None)):
			if self.market == "bigweb":
				return self.to_safe(card_price, card)
			
			return card
	
	"""
	Honestly, I can't think of a way to do the same thing as
	this function but with a MongoDB query
	"""
	def find_card_with_set_number(self, set_number: str) -> Optional[Card]:
		return next((card for card in self.all_cards for set in card["sets"][self.set_locale] if set["set_number"] in set_number), None)
	
	def to_safe(self, card_price: CardPrice, card: Card) -> Optional[Card]:
		if "トークン" in card_price["name"] and not card["konami_id"] in self.token_in_name_list \
		or self.is_in(card_price["set_number"], self.token_prefix_list):
			card = self.coll.find_one({"konami_id": 0})
		elif self.is_in(card_price["set_number"], self.unsafe_prefix_list) \
		or self.is_in(card_price["comment"], self.unsafe_comment_list) \
		or not card_price["comment"] or card_price["rarity"] == "-":
			return None
		
		if card["name"]["ja"] != card_price["name"] and card["konami_id"] != 0:
			logger.debug(f"{card_price}\n!=\n{card}")
		
		return card
	
	def is_in(self, string: str, arr: list) -> bool:
		return any(e in string for e in arr)