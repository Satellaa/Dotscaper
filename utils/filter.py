
class Filter():
	
	@staticmethod
	def create_name_filter(language: str, query: str) -> dict:
		return {
			"$search": {
				"index": f"name_search",
				"text": {
					"query": query,
					"path": f"name.{language}",
					"fuzzy": {
						"maxEdits": 1
					}
				}
			}
		}