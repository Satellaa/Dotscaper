from time import sleep
from typing import Callable, Optional

from requests import Response
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)


def get_response(get: Callable[..., Response], url: str) -> Optional[Response]:
    for i in range(10):
        try:
            response = get(url)
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

    return None
