import argparse
import os
import sys

import trio
from dotenv import load_dotenv

from executor import Executor

load_dotenv()


class CardManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Manage card information and prices.")
        self.parser.add_argument(
            "--init",
            action="store_true",
            help="Upsert card information and prices"
        )
        self.parser.add_argument(
            "--update-card-info",
            action="store_true",
            help="Upsert card information from YAML Yugi or Yugipedia"
        )
        self.parser.add_argument(
            "--update-card-prices",
            action="store_true",
            help="Upsert card prices from Bigweb or TCG Corner"
        )
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

    def handle_choice(self, update_info=False, update_prices=False):
        if update_info:
            source = self.get_user_choice(
                "Card information", [
                    "YAML Yugi", "Yugipedia"])
            self.update_card_info(source)
        elif update_prices:
            source = self.get_user_choice(
                "Card prices", ["Bigweb", "TCG Corner"])
            self.update_card_prices(source)

    def get_user_choice(self, update_type, sources):
        print(f"Select the update source for {update_type}:")
        for i, source in enumerate(sources, 1):
            print(f"{i}. Only update from {source}")
        print(f"{len(sources) + 1}. Update both")
        print(f"{len(sources) + 2}. Quit")
        choice = input("Enter your selection: ")

        if int(choice) == len(sources) + 2:
            sys.exit(0)

        return choice

    def update_card_info(self, choice):
        if choice == "1":
            print("Upsert card information from YAMI Yugi...")
            self.executor.update_cards()
        elif choice == "2":
            print("Upsert card information from Yugipedia...")
            self.executor.update_cards(False, True)
        elif choice == "3":
            print("Upsert card information from both YAMI Yugi and Yugipedia...")
            self.executor.update_cards(True, True)
        else:
            print("Invalid selection.")

    def update_card_prices(self, choice):
        if choice == "1":
            print("Upsert card prices from Bigweb...")
            trio.run(self.executor.update_prices)
        elif choice == "2":
            print("Upsert card prices from TCG Corner...")
            trio.run(self.executor.update_prices, False, True)
        elif choice == "3":
            print("Upsert card prices from both Bigweb and TCG Corner...")
            trio.run(self.executor.update_prices, True, True)
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    manager = CardManager()
    manager.setup_executor()
    if manager.args.init:
        manager.update_card_info("3")
        manager.update_card_prices("3")
    elif manager.args.update_card_info:
        manager.handle_choice(update_info=True)
    elif manager.args.update_card_prices:
        manager.handle_choice(update_prices=True)
