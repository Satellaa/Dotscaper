import requests
from utils.string_manip import parse_and_expand_ruby
from utils.card import Card, Name, Sets, remove_duplicates_sets
from typing import Optional
from . fetch import get_response

"""
Keep in mind that we will only obtain
the data required for the Kitt bot.
"""
class YAMLYugiScraper:
	def __init__(self):
		self.yaml_yugi_endpoint = "https://raw.githubusercontent.com/DawnbrandBots/yaml-yugi/aggregate/cards.json"
	
	def scrape(self) -> Optional[list[Card]]:
		response = get_response(requests.get, self.yaml_yugi_endpoint)
		if response:
			return self.parse_cards(response.json())
	
	def parse_cards(self, raw_cards: list[dict]) -> list[Card]:
		cards = []
		for raw_card in raw_cards:
			konami_id = raw_card.get("konami_id", 0)
			if not konami_id:
				continue
			
			ja_sets = remove_duplicates_sets(self.parse_ja_sets(raw_card))
			password = raw_card.get("password", 0)
			en_name, ja_name = self.parse_names(raw_card)
			
			if password == password:
				password = int(password)
			
			card = Card(
				name=Name(en=en_name, ja=ja_name),
				konami_id=konami_id,
				password=password,
				sets=Sets(ja=ja_sets, ae=[])
			)
			cards.append(card)
		
		return cards
	
	def parse_ja_sets(self, raw_card) -> list:
		try:
			return [{"set_number": sets["set_number"]} for sets in raw_card["sets"]["ja"]]
		except KeyError:
			return []
	
	def parse_names(self, raw_card) -> (str, str):
		en_name = raw_card["name"]["en"]
		ja_name = raw_card["name"]["ja"]
		ja_name = parse_and_expand_ruby(ja_name) if ja_name else ""
		
		return en_name, ja_name
	
	
	