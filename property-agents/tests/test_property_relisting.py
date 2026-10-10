import unittest

import engine


class PropertyRelistingSafetyTests(unittest.TestCase):
    def test_changed_listing_id_same_exact_address_is_relisting(self):
        previous = {
            "Listing Status": "Removed",
            "Lead ID": "OP-old-id",
            "Source": "open-properties/rightmove",
            "Source URL": "https://rightmove.co.uk/old-listing?utm_source=x",
            "Property Address": "12 High Street",
            "Postcode": "CR0 1AA",
        }
        current = {
            "Lead ID": "OP-new-id",
            "Source": "open-properties/rightmove",
            "Source URL": "https://rightmove.co.uk/new-listing",
            "Property Address": " 12 HIGH STREET ",
            "Postcode": "cr0 1aa",
        }
        is_relisting, confidence = engine.classify_relisting(previous, current)
        self.assertTrue(is_relisting)
        self.assertEqual(confidence, "High")

    def test_same_postcode_different_house_number_is_not_relisting(self):
        previous = {
            "Listing Status": "Removed",
            "Lead ID": "OP-old-id",
            "Source": "open-properties/rightmove",
            "Property Address": "12 High Street",
            "Postcode": "CR0 1AA",
        }
        current = {
            "Lead ID": "OP-new-id",
            "Source": "open-properties/rightmove",
            "Property Address": "14 High Street",
            "Postcode": "CR0 1AA",
        }
        self.assertEqual(engine.classify_relisting(previous, current), (False, "Unknown"))

    def test_area_without_street_number_does_not_match_relisting(self):
        previous = {"Listing Status": "Removed", "Area": "Croydon", "Postcode": "CR0 1AA"}
        current = {"Area": "Croydon", "Postcode": "CR0 1AA"}
        self.assertEqual(engine.classify_relisting(previous, current), (False, "Unknown"))

    def test_not_removed_listing_is_not_classified_as_relisting(self):
        previous = {
            "Listing Status": "Active",
            "Property Address": "12 High Street",
            "Postcode": "CR0 1AA",
            "Source URL": "https://rightmove.co.uk/old",
        }
        current = {
            "Property Address": "12 High Street",
            "Postcode": "CR0 1AA",
            "Source URL": "https://rightmove.co.uk/new",
        }
        self.assertEqual(engine.classify_relisting(previous, current), (False, "Unknown"))


if __name__ == "__main__":
    unittest.main()
