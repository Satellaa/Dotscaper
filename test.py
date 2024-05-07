import unittest
from unittest.mock import patch

from scrapers.yaml_yugi import YAMLYugiScraper
from scrapers.yugipedia import YugipediaScraper


class TestYugipediaScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = YugipediaScraper()
        self.sample_raw_cards = {
            "query": {
                "results": {
                    "Sample Card": {
                        "printouts": {
                            "Card number": ["ABCD-123456"],
                            "English name": ["Sample Card"],
                            "Japanese base name": ["サンプルカード"],
                            "Database ID": [123456],
                            "Password": ["987654"]
                        }
                    }
                }
            }
        }

        self.sample_parsed_cards = [
            {
                "konami_id": 123456,
                "password": 987654,
                "name": {"en": "Sample Card", "ja": "サンプルカード"},
                "sets": {"ae": [{"set_number": "ABCD-123456"}]}
            }
        ]

    def test_parse_cards(self):
        result = self.scraper.parse_cards(self.sample_raw_cards, "ae")
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")
            self.assertEqual(result[0]["name"]["en"], "Sample Card", "The English name should match")
            self.assertEqual(result[0]["name"]["ja"], "サンプルカード", "The Japanese name should match")
            self.assertEqual(result[0]["konami_id"], 123456, "The Konami ID should match")
            self.assertEqual(result[0]["password"], 987654, "The password should match")
            self.assertIn("ae", result[0]["sets"], "There should be information about the Asian English set")
            self.assertEqual(result[0]["sets"]["ae"][0]["set_number"], "ABCD-123456", "The set number should match")

    @patch("scrapers.yugipedia.YugipediaScraper.scrape")
    def test_scrape_asian_english_sets(self, mock_scrape):
        mock_scrape.return_value = self.sample_parsed_cards
        result = self.scraper.scrape_asian_english_sets()
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")

    @patch("scrapers.yugipedia.YugipediaScraper.scrape")
    def test_scrape_counters(self, mock_scrape):
        mock_scrape.return_value = self.sample_parsed_cards
        result = self.scraper.scrape_counters()
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")

    @patch("scrapers.yugipedia.YugipediaScraper.scrape")
    def test_scrape_tokens(self, mock_scrape):
        mock_scrape.return_value = self.sample_parsed_cards
        result = self.scraper.scrape_tokens()
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")

    @patch("scrapers.yugipedia.YugipediaScraper.scrape")
    def test_scrape_illegal_cards(self, mock_scrape):
        mock_scrape.return_value = self.sample_parsed_cards
        result = self.scraper.scrape_illegal_cards()
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")

    def tearDown(self):
        self.scraper.session.close()


class TestYAMLYugiScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = YAMLYugiScraper()
        self.sample_raw_cards = [
            {
                "konami_id": 123456,
                "password": 987654,
                "name": {"en": "Sample Card", "ja": "サンプルカード"},
                "sets": {"ja": [{"set_number": "ABCD-123456"}]}
            }
        ]

    def test_parse_cards(self):
        result = self.scraper.parse_cards(self.sample_raw_cards)
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")
            self.assertEqual(result[0]["konami_id"], 123456, "The Konami ID should match")
            self.assertEqual(result[0]["password"], 987654, "The password should match")
            self.assertEqual(result[0]["name"]["en"], "Sample Card", "The English name should match")
            self.assertEqual(result[0]["name"]["ja"], "サンプルカード", "The Japanese name should match")
            self.assertEqual(result[0]["sets"]["ja"][0]["set_number"], "ABCD-123456", "The set number should match")

    @patch("scrapers.yaml_yugi.YAMLYugiScraper.scrape")
    def test_scrape(self, mock_scrape):
        mock_scrape.return_value = self.sample_raw_cards
        result = self.scraper.scrape()
        self.assertIsInstance(result, list, "The result should be a list")
        if result:
            self.assertIsInstance(result[0], dict, "The first element of the result should be a dict")

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
