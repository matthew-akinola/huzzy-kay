import unittest
from typing import List
import sys

# sys.path.append("/home/cm/Documents/HNG INTERNSHIP/BACKEND/vipcustomer.api/app")
from core.sources.celebrity_api.celebrity_api import CelebrityApi
from core.sources.forbes_scraper.forbes import ForbesVip
from core.sources.sports_source.services import SearchService
from core.sources.wikipedia.scrape import Wiki_Source
from core.data.dataclass import DataClass


class TestProcess(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.user_input = {"name": "Joel", "age": 22}
        cls.data_list = [[{"name": "Joel James", "age": 22, "vip_score": 48, "is_vip": True}],
        [{"name": "Joel Favour", "age": 42, "vip_score": 28}],
        [{"name": "Joel Klint", "age": 82, "vip_score": 48}],
        [{"name": "Joel Boss", "age": 22, "vip_score": 88}]
        ]

    def test_wikipedia_source(self):
        self.assertIsInstance(Wiki_Source().process(self.user_input), List)

    def test_forbes_source(self):
        self.assertIsInstance(ForbesVip().process(self.user_input), List)

    def test_sport_source(self):
        self.assertIsInstance(SearchService().process(self.user_input), List)

    def test_celebrity_source(self):
        self.assertIsInstance(CelebrityApi().process(self.user_input), List)

    def test_dataclass(self):
        self.assertIsInstance(DataClass(self.data_list, **self.user_input).initiate(), List)

if __name__ == "__main__":
    unittest.main()