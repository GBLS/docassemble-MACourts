import unittest
from docassemble.base.util import Address, LatitudeLongitude
from ..macourts import MACourtList
from pathlib import Path

class TestCourtFinder(unittest.TestCase):
    def setUp(self):
      data_path = data_path=Path(__file__).resolve().parent.joinpath('../data/sources')
      self.all_courts = MACourtList(data_path=data_path)
      self.all_courts.load_courts(
          ['housing_courts','bmc','district_courts','superior_courts','land_court','juvenile_courts','probate_and_family_courts','appeals_court'],
      )
      self.court_types = ["District Court", "Boston Municipal Court","Housing Court","Superior Court", "Probate and Family Court","Juvenile Court","Land Court"]

    def test_search_in_bristol(self):
        address = Address(address="91 Highland Road", city="Swansea", state="Massachusetts", county="Bristol County", zip="02777")
        court_list = self.all_courts.matching_probate_and_family_court(address)
        self.assertGreaterEqual(len(court_list), 1)
        self.assertEqual(list(court_list)[0].name, "Bristol Probate and Family Court")

    def test_search_boston(self):
        address = Address(address="1234 Soldiers Field Road", city="Boston", county="Suffolk County", 
            state="Massachusetts", zip="02135", 
            location=LatitudeLongitude(latitude=42.3641126, longitude=-71.1364048),
            norm=Address(address="1234 Soliders Field Road", city="Boston", county="Suffolk Courty", 
                state="Massachusetts", zip="02135"))
        court_list = self.all_courts.matching_courts(address, court_types=self.court_types)
        court_strings = [str(court.name) for court in court_list]
        print(court_strings)
        self.assertEqual(len(court_list), 6)
        self.assertIn("Brighton Division, Boston Municipal Court", court_strings)
        self.assertIn("Suffolk County Superior Court", court_strings)
        self.assertIn("Eastern Housing Court", court_strings)
        self.assertIn("Suffolk Probate and Family Court", court_strings)
        self.assertIn("Boston Juvenile Court", court_strings)
        self.assertIn("Land Court", court_strings)

if __name__ == "__main__":
    unittest.main()