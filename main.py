import argparse
import os
import sys

import trio
from dotenv import load_dotenv

from module.executor import Executor

load_dotenv()


class CardManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Manage card information and prices.")
        self.parser.add_argument("--update-card-info", action="store_true", help="Upsert card information from YAML Yugi or Yugipedia")
        self.parser.add_argument("--update-card-prices", action="store_true", help="Upsert card prices from selected market")
        self.args = self.parser.parse_args()
        self.executor = None

    def setup_executor(self):
        print("Setup MongoDB...")
        print(
            """Tips: To avoid having to enter the URI, DB_NAME, and COLL_NAME again,
			you can add them to the .env file."""
        )
        uri = os.getenv("URI") or input("Enter your MongoDB URI: ")
        db_name = os.getenv("DB_NAME") or input(
            "Enter your MongoDB Database name: ")
        coll_name = os.getenv("COLL_NAME") or input(
            "Enter your MongoDB Collection name: ")

        self.executor = Executor(uri, db_name, coll_name)

    def update_card_info(self):
        source = self.get_user_choice(
            "Card information", ["YAML Yugi", "Yugipedia", "All"])
        print(f"Updating card information from {source}...")
        trio.run(self.executor.update_cards, source)

    def update_card_prices(self):
        sources = ["Bigweb", "Yuyutei", "TCG Corner"]
        source = self.get_user_choice("Card prices", sources + ["All"])
        if source == "All":
            markets_to_update = sources
        else:
            markets_to_update = [source]

        print(f"Updating prices from {', '.join(markets_to_update)}...")
        trio.run(self.executor.update_prices, markets_to_update)

    def get_user_choice(self, update_type: str, sources: list[str]):
        while True:
            self.print_menu(update_type, sources)
            choice = input("Enter your selection: ")
            try:
                if int(choice) == len(sources) + 1:
                    sys.exit(0)
                elif (int(choice) - 1) < len(sources):
                    return sources[int(choice) - 1]
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a number corresponding to the options.")

            print("Please try again")

    def print_menu(self, update_type: str, sources: list[str]):
        print(f"Select the update source for {update_type}:")
        for i, source in enumerate(sources, 1):
            print(f"{i}. Update from {source}")
        print(f"{len(sources) + 1}. Exit")


if __name__ == "__main__":
    manager = CardManager()
    manager.setup_executor()
    if manager.args.update_card_info:
        manager.update_card_info()
    elif manager.args.update_card_prices:
        manager.update_card_prices()
    else:
        print("No action specified. Use --help to see available options.")
        sys.exit(1)
