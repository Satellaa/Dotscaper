import requests
from requests import Response, Session
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from typing import Optional, Callable
from time import sleep

def get_response(get: Callable[..., Response], url: str, params: dict={}) -> Optional[Response]:
	for i in range(10):
		try:
			response = get(url, params=params)
			response.raise_for_status()
			return response
		except HTTPError as e:
			print(f"HTTP Error: {e}")
		except ConnectionError as e:
			print(f"Connection Error: {e}")
		except Timeout as e:
			print(f"Timeout Error: {e}")
		except RequestException as e:
			print(f"Request Exception: {e}")
		
		print(f"\nFailure: {i + 1}")
		print("Attempt to try again...\n")
		
		sleep(10)