from typing import TypedDict

class CardPrice(TypedDict):
	id: int
	price: int
	name: str
	set_number: str
	rarity: str
	condition: str
	status: str
	last_modified: int
	comment: str # Only used for bigweb, to check the validity of card price

class CardPrices(TypedDict):
	bigweb: list[CardPrice]
	yuyutei: list[CardPrice]
	tcg_corner: list[CardPrice]

class Name(TypedDict):
	en: str
	ja: str

class Set(TypedDict):
	set_number: str

class Sets(TypedDict):
	ja: list[Set]
	ae: list[Set]

class Card(TypedDict):
	name: Name
	konami_id: int
	password: int
	sets: Sets
	card_prices: CardPrices

def remove_duplicates_sets(sets: list[dict]) -> list:
	seen = set()
	unique = []
	
	for set_card in sets:
		if set_card["set_number"] not in seen and set_card["set_number"] != "" and set_card["set_number"] != " ":
			unique.append(set_card)
			seen.add(set["set_number"])
	
	return unique