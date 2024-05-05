import requests
import time
from urllib import parse
from utils.card import Card, Name, Sets
from utils.safe import get
from platform import python_version
from typing import Optional
from . fetch import get_response

"""
We will have to use Yugipedia because YAML Yugi does not have
some things, like set numbers in Asian English.
"""
class YugipediaScraper:
	def __init__(self):
		self.session = requests.Session()
		# Yugipedia requires you to leave service and contact information.
		self.session.headers.update({"User-Agent": f"https://github.com/Satellaa/Dotscaper.git requests/{requests.__version__} py/{python_version()}"})
		
		self.asian_english_endpoint = self.create_yugipedia_endpoint("Asian-English", limit=5000)
		self.tokens_endpoint = self.create_yugipedia_endpoint("Japanese", "[[Set contains.English name::Token]]")
		self.illegal_cards_endpoint = self.create_yugipedia_endpoint("Japanese", "[[Set contains.OCG status::Illegal]]")
		self.counters_endpoint = self.create_yugipedia_endpoint("Japanese", "[[Set contains.Card type::Counter]]")
		
		self.scrape_funs = [
			self.scrape_asian_english_sets,
			self.scrape_counters,
			self.scrape_tokens,
			self.scrape_illegal_cards
		]
	
	def scrape_all(self) -> list[Card]:
		cards = []
		for fun in self.scrape_funs:
			if (result := fun()):
				cards += result
			time.sleep(2)
		
		return cards
	
	def scrape_asian_english_sets(self) -> Optional[list[Card]]:
		return self.scrape(self.asian_english_endpoint, "ae")
	
	def scrape_counters(self) -> Optional[list[Card]]:
		return self.scrape(self.counters_endpoint)
	
	def scrape_tokens(self) -> Optional[list[Card]]:
		return self.scrape(self.tokens_endpoint)
	
	def scrape_illegal_cards(self) -> Optional[list[Card]]:
		return self.scrape(self.illegal_cards_endpoint)
	
	def scrape(self, url: str, set_language: str="ja") -> Optional[list[Card]]:
		response = get_response(self.session.get, url)
		if response:
			return self.parse_cards(response.json(), set_language)
	
	def parse_cards(self, raw_cards: list[dict], set_language: str) -> list[Card]:
		cards = []
		for raw_card in raw_cards["query"]["results"].values():
			printouts = raw_card["printouts"]
			set_number = get(printouts["Card number"], 0, [])
			en_name = get(printouts["English name"], 0, "")
			ja_name = get(printouts["Japanese base name"], 0, "")
			konami_id = 0 if en_name == "Token" else get(printouts["Database ID"], 0, -1) 
			password = 0 if en_name == "Token" else get(printouts["Password"], 0, -1)
		
			if (not set_number and not ja_name) or (not en_name and konami_id < 0):
				continue
			
			if isinstance(password, str):
				password = int(password)
			if isinstance(konami_id, str):
				konami_id = int(konami_id)
			
			card = Card(
				name=Name(en=en_name, ja=ja_name),
				konami_id=konami_id,
				password=password,
				sets={}
			)
			if set_number:
				set_number = [{"set_number": set_number}]
			
			card["sets"][set_language] = set_number
			
			cards.append(card)
		return cards
	
	def create_yugipedia_endpoint(self, local: str, conditions: str="", limit: int=500) -> str:
		params = {
			"action": "ask",
			"query": f"[[-Has subobject.Locality::{local}]] {conditions}|?Card number|?Set contains.English name|?Set contains.Japanese base name|?Set contains.Database ID|?Set contains.Password|limit={limit}|offset=0",
			"format": "json"
		}
		
		return f"https://yugipedia.com/api.php?{parse.urlencode(params)}"